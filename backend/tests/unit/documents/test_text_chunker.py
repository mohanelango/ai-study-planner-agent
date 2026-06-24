import unittest

from app.infrastructure.document_processing.pdf_extractor import PageText
from app.infrastructure.document_processing.text_chunker import TextChunker


class TextChunkerTestCase(unittest.TestCase):
    def test_chunker_splits_long_text_with_overlap_and_order(self) -> None:
        text = "a" * 250
        chunks = TextChunker(chunk_size_chars=100, overlap_chars=20).chunk_pages([PageText(1, text)], text)
        self.assertEqual([chunk.chunk_index for chunk in chunks], [0, 1, 2])
        self.assertEqual(chunks[0].char_start, 0)
        self.assertEqual(chunks[1].char_start, 80)
        self.assertEqual(chunks[2].char_start, 160)
        self.assertTrue(all(len(chunk.text) <= 100 for chunk in chunks))


if __name__ == "__main__":
    unittest.main()

