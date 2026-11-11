import unittest

from game.call_summary import CallSummary


class TestCallSummary(unittest.TestCase):
    def test_records_lines_in_order(self):
        summary = CallSummary()
        summary.record_speech("partner", "Hi! What can I get you?")
        summary.record_speech("student", "A latte, please.")
        self.assertEqual(
            [("partner", "Hi! What can I get you?"), ("student", "A latte, please.")],
            [(line.speaker, line.text) for line in summary.transcript],
        )

    def test_same_utterance_id_updates_line(self):
        summary = CallSummary()
        summary.record_speech("student", "A lat", "u1")
        summary.record_speech("student", "A latte, please.", "u1")  # speech recognition refined it
        self.assertEqual(1, len(summary.transcript))
        self.assertEqual("A latte, please.", summary.transcript[0].text)


if __name__ == "__main__":
    unittest.main()
