import json
import os
import tempfile
import unittest

from snake_game import scores
from snake_game.terminal import parse_keys


class ParseKeysTests(unittest.TestCase):
    def test_arrows_csi_and_ss3(self):
        self.assertEqual(parse_keys("\x1b[A\x1b[B\x1b[C\x1b[D"), ["UP", "DOWN", "RIGHT", "LEFT"])
        self.assertEqual(parse_keys("\x1bOA\x1bOD"), ["UP", "LEFT"])

    def test_several_keys_in_one_read(self):
        self.assertEqual(parse_keys("\x1b[Aw\x1b[Dq"), ["UP", "w", "LEFT", "q"])

    def test_lone_escape_and_enter(self):
        self.assertEqual(parse_keys("\x1b"), ["ESC"])
        self.assertEqual(parse_keys("\r\n "), ["ENTER", "ENTER", "SPACE"])

    def test_unknown_sequences_do_not_leak_letters(self):
        # F5 = ESC [ 1 5 ~ ; must not turn into '1', '5'
        self.assertEqual(parse_keys("\x1b[15~x"), ["x"])

    def test_uppercase_is_lowered(self):
        self.assertEqual(parse_keys("WQ"), ["w", "q"])


class ScoresTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["SNAKE_GAME_HOME"] = self.tmp.name

    def tearDown(self):
        os.environ.pop("SNAKE_GAME_HOME", None)
        self.tmp.cleanup()

    def test_record_keeps_only_best(self):
        self.assertTrue(scores.record("easy", 50))
        self.assertFalse(scores.record("easy", 30))
        self.assertTrue(scores.record("easy", 80))
        self.assertEqual(scores.load(), {"easy": 80})

    def test_corrupt_file_is_ignored(self):
        with open(scores.scores_path(), "w") as f:
            f.write("{not json")
        self.assertEqual(scores.load(), {})
        self.assertTrue(scores.record("hard", 10))
        with open(scores.scores_path()) as f:
            self.assertEqual(json.load(f), {"hard": 10})


if __name__ == "__main__":
    unittest.main()
