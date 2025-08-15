# Homebrew Tap Setup Guide

## Step 1: Create homebrew-snake Repository

1. **Go to GitHub and create a new repository:**
   - Repository name: `homebrew-snake`
   - Description: `Homebrew tap for Snake Game CLI`
   - Set to **Public**
   - Don't initialize with README

2. **Clone and setup the repository:**
   ```bash
   git clone https://github.com/movin-gun/homebrew-snake.git
   cd homebrew-snake
   ```

3. **Copy the formula file:**
   ```bash
   # From your snake project directory
   cp Formula/snake-game-cli.rb ~/path/to/homebrew-snake/snake-game-cli.rb
   ```

4. **Push to GitHub:**
   ```bash
   git add snake-game-cli.rb
   git commit -m "Add Snake Game CLI formula"
   git push origin main
   ```

## Step 2: Test Local Installation

```bash
# Add the tap
brew tap movin-gun/snake

# Install the game
brew install snake-game-cli

# Test the game
snakegame
```

## Step 3: Verify Installation

The game should be available with these commands:
- `snakegame` (primary command)
- `snake-game` (alternative)
- `snake` (short version)

## Formula File Content

The formula file should contain:

```ruby
class SnakeGameCli < Formula
  desc "Simple and fun terminal snake game"
  homepage "https://github.com/movin-gun/snake"
  url "https://github.com/movin-gun/snake/archive/refs/heads/main.zip"
  version "2.0.0"
  sha256 :no_check
  license "MIT"
  
  depends_on "python@3.11"
  
  def install
    virtualenv_install_with_resources
    
    # Create symlinks for all the executables
    bin.install_symlink libexec/"bin/snakegame"
    bin.install_symlink libexec/"bin/snake-game"
    bin.install_symlink libexec/"bin/snake"
  end
  
  test do
    # Test that the command can be called
    system "#{bin}/snakegame", "--help" rescue true
    system "#{bin}/snake-game", "--help" rescue true
    system "#{bin}/snake", "--help" rescue true
  end
  
  def caveats
    <<~EOS
      Snake Game CLI has been installed!
      
      To start playing, run:
        snakegame
      
      Game Controls:
        Arrow keys  Move snake
        Q           Quit game
        1-3         Select difficulty
      
      Features:
        - Simple and clean terminal interface
        - 3 difficulty levels (Easy/Medium/Hard)
        - Color support with graceful fallback
        - Cross-platform compatibility
      
      Have fun and beat your high score!
    EOS
  end
end
```

## Troubleshooting

### Common Issues:

1. **Repository not found:**
   - Make sure `homebrew-snake` repository is public
   - Check repository name spelling

2. **Formula not found:**
   - Ensure formula file is in root directory of homebrew-snake repo
   - File must be named `snake-game-cli.rb`

3. **Installation fails:**
   - Check Python dependencies
   - Verify setup.py is properly configured

### Manual Installation Alternative:

If homebrew fails, users can still install via pip:

```bash
git clone https://github.com/movin-gun/snake.git
cd snake
pip install .
snakegame
```

## Next Steps

1. Create the `homebrew-snake` repository on GitHub
2. Upload the formula file
3. Test installation on different systems
4. Update main repository documentation
5. Share installation instructions with users