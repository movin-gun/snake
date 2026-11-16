# Snake Game CLI - Windows installer / quick play
#   play once : irm https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1 | iex
#   install   : & ([scriptblock]::Create((irm https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1))) -Mode install
param(
    [ValidateSet("play", "install", "uninstall")]
    [string]$Mode = "play"
)

$ErrorActionPreference = "Stop"
$ZipUrl  = "https://github.com/movin-gun/snake/archive/refs/heads/main.zip"
$GameDir = Join-Path $env:LOCALAPPDATA "snake-game\app"
$BinDir  = Join-Path $env:LOCALAPPDATA "snake-game\bin"

function Info($m) { Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "[ OK ] $m" -ForegroundColor Green }

# Find a real Python 3.7+. The Microsoft Store "python" stub fails the version check.
function Find-Python {
    foreach ($cand in @(@("py", "-3"), @("python"), @("python3"))) {
        $exe = $cand[0]
        if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
        $rest = @($cand | Select-Object -Skip 1)
        & $exe @rest -c "import sys; sys.exit(sys.version_info < (3, 7))" 2>$null
        if ($LASTEXITCODE -eq 0) { return ,$cand }
    }
    throw "Python 3.7+ is required. Install it from https://www.python.org/downloads/ and retry."
}

function Get-Source {
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("snake-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $tmp | Out-Null
    Invoke-WebRequest -Uri $ZipUrl -OutFile (Join-Path $tmp "snake.zip") -UseBasicParsing
    Expand-Archive -Path (Join-Path $tmp "snake.zip") -DestinationPath $tmp
    return $tmp
}

switch ($Mode) {
    "uninstall" {
        Remove-Item -Recurse -Force $GameDir, $BinDir -ErrorAction SilentlyContinue
        Ok "Removed. (Best scores are kept in $env:APPDATA\snake-game)"
    }
    "install" {
        $py = Find-Python
        Info "Downloading Snake Game..."
        $tmp = Get-Source
        try {
            Remove-Item -Recurse -Force $GameDir -ErrorAction SilentlyContinue
            New-Item -ItemType Directory -Force -Path $GameDir, $BinDir | Out-Null
            Copy-Item -Recurse (Join-Path $tmp "snake-main\snake_game") $GameDir
        } finally {
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }
        $pyCmd = ($py -join " ")
        "@echo off`r`nset `"PYTHONPATH=$GameDir;%PYTHONPATH%`"`r`n$pyCmd -m snake_game %*`r`n" |
            Out-File -FilePath (Join-Path $BinDir "snakegame.cmd") -Encoding ascii

        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if (($userPath -split ";") -notcontains $BinDir) {
            [Environment]::SetEnvironmentVariable("Path", ($userPath.TrimEnd(";") + ";" + $BinDir), "User")
            Info "Added $BinDir to your user PATH (open a new terminal to use it)."
        }
        Ok "Installed. Run: snakegame"
    }
    default {
        $py = Find-Python
        $tmp = Get-Source
        try {
            Push-Location (Join-Path $tmp "snake-main")
            $exe = $py[0]; $rest = @($py | Select-Object -Skip 1)
            & $exe @rest -m snake_game
        } finally {
            Pop-Location
            Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
        }
    }
}
