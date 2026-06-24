import unittest

from app.infrastructure.document_processing.text_cleaner import TextCleaner


class TextCleanerTestCase(unittest.TestCase):
    def test_clean_normalizes_whitespace(self) -> None:
        dirty = "Title\r\n\r\n\r\n  Some     text   \n\n\nNext line "
        cleaned = TextCleaner().clean(dirty)
        self.assertEqual(cleaned, "Title\n\nSome text\n\nNext line")


if __name__ == "__main__":
    unittest.main()

