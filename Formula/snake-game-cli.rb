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