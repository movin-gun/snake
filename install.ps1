# Snake Game CLI - Windows PowerShell Installer
# Usage: Invoke-WebRequest -Uri "https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1" | Invoke-Expression
# or: iwr "https://raw.githubusercontent.com/movin-gun/snake/main/install.ps1" | iex

param(
    [string]$Mode = "play"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Status { 
    Write-Host "[INFO] $args" -ForegroundColor Blue 
}
function Write-Success { 
    Write-Host "[SUCCESS] $args" -ForegroundColor Green 
}
function Write-Error { 
    Write-Host "[ERROR] $args" -ForegroundColor Red 
}

if ($Mode -eq "install") {
    Write-Host "🐍 Snake Game CLI - Installing..." -ForegroundColor Yellow
    
    # Check if Python is available
    $pythonCmd = $null
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pythonCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pythonCmd = "python"
    } else {
        Write-Error "Python is required but not found. Please install Python 3.7+ first."
        exit 1
    }
    
    # Create install directory
    $installDir = "$env:USERPROFILE\.local\bin"
    $snakeDir = "$env:USERPROFILE\.snake-game"
    
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
    New-Item -ItemType Directory -Force -Path $snakeDir | Out-Null
    
    # Download and install
    Write-Status "Downloading Snake Game..."
    $tempDir = New-TemporaryFile | %{ rm $_; mkdir $_ }
    
    Invoke-WebRequest -Uri "https://github.com/movin-gun/snake/archive/main.zip" -OutFile "$tempDir\snake.zip"
    Expand-Archive -Path "$tempDir\snake.zip" -DestinationPath $tempDir
    
    # Copy game files
    Write-Status "Installing game files..."
    Copy-Item -Path "$tempDir\snake-main\*" -Destination $snakeDir -Recurse -Force
    
    # Create batch file executable
    Write-Status "Creating executable..."
    $batchContent = @"
@echo off
cd /d "$snakeDir"
$pythonCmd snake_game\game.py
"@
    
    $batchContent | Out-File -FilePath "$installDir\snakegame.bat" -Encoding ASCII
    
    # Cleanup
    Remove-Item -Path $tempDir -Recurse -Force
    
    Write-Success "Snake Game CLI installed successfully!"
    Write-Host ""
    Write-Host "🎮 To play the game, run:" -ForegroundColor Yellow
    Write-Host "   snakegame" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Make sure the install directory is in your PATH:" -ForegroundColor Blue
    Write-Host "   $installDir" -ForegroundColor Green
    
} else {
    Write-Host "🐍 Snake Game CLI - Quick Play" -ForegroundColor Yellow
    
    # Quick play mode (default)
    Write-Status "Downloading and starting game..."
    $tempDir = New-TemporaryFile | %{ rm $_; mkdir $_ }
    
    Invoke-WebRequest -Uri "https://github.com/movin-gun/snake/archive/main.zip" -OutFile "$tempDir\snake.zip"
    Expand-Archive -Path "$tempDir\snake.zip" -DestinationPath $tempDir
    
    Write-Status "Starting game..."
    Set-Location "$tempDir\snake-main"
    
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        & python3 snake_game\game.py
    } else {
        & python snake_game\game.py
    }
    
    # Cleanup
    Set-Location $env:USERPROFILE
    Remove-Item -Path $tempDir -Recurse -Force
    Write-Success "Thanks for playing!"
}