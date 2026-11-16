# Homebrew formula (HEAD-only until a tagged release exists).
#   brew install --HEAD ./Formula/snake-game-cli.rb
# To ship a stable formula, tag a release (e.g. v3.0.0) and add:
#   url "https://github.com/movin-gun/snake/archive/refs/tags/v3.0.0.tar.gz"
#   sha256 "<shasum -a 256 of that tarball>"
class SnakeGameCli < Formula
  include Language::Python::Virtualenv

  desc "Classic snake game for the terminal"
  homepage "https://github.com/movin-gun/snake"
  head "https://github.com/movin-gun/snake.git", branch: "main"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "snakegame", shell_output("#{bin}/snakegame --version")
  end
end
