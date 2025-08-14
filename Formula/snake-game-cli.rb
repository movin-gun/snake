class SnakeGameCli < Formula
  desc "A classic snake game for terminal/CLI"
  homepage "https://github.com/anthropics/snake-game-cli"
  url "https://github.com/anthropics/snake-game-cli/archive/v1.0.0.tar.gz"
  sha256 "0000000000000000000000000000000000000000000000000000000000000000" # This would be replaced with actual SHA256
  license "MIT"
  
  depends_on "python@3.11"
  
  def install
    virtualenv_install_with_resources
    
    # Create symlinks for the executables
    bin.install_symlink libexec/"bin/snake-game"
    bin.install_symlink libexec/"bin/snake"
  end
  
  test do
    # Test that the command can be called and shows help/version info
    system "#{bin}/snake-game", "--version"
  end
  
  def caveats
    <<~EOS
      🐍 Snake Game CLI has been installed!
      
      To start playing, run:
        snake-game
      
      Or use the short command:
        snake
      
      Game Controls:
        ↑ ↓ ← →  Arrow keys to move
        Q        Quit game
        1-5      Navigate menus
      
      Features:
        • Multiple difficulty levels
        • Beautiful ASCII graphics
        • Score tracking
        • Cross-platform support
      
      Have fun and try to beat your high score! 🏆
    EOS
  end
end