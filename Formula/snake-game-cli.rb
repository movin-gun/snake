class SnakeGameCli < Formula
  desc "A classic snake game for terminal/CLI"
  homepage "https://github.com/movin-gun/snake"
  url "https://github.com/movin-gun/snake/archive/refs/heads/main.zip"
  version "1.0.0"
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
      🐍 Snake Game CLI has been installed!
      
      To start playing, use any of these commands:
        snakegame    (recommended)
        snake-game
        snake
      
      Game Controls:
        ↑ ↓ ← →  Arrow keys to move
        Q        Quit game
        1-5      Navigate menus
      
      Features:
        • Beautiful ASCII logo screen
        • Multiple difficulty levels
        • Game instructions and high scores
        • Korean/English interface
        • Cross-platform support
      
      Have fun and try to beat your high score! 🏆
    EOS
  end
end