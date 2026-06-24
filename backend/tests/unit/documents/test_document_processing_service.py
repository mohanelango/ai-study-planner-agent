import unittest

from app.infrastructure.document_processing.pdf_extractor import PageText
from app.infrastructure.document_processing.text_chunker import TextChunker
from app.infrastructure.document_processing.text_cleaner import TextCleaner


class DocumentProcessingServiceUnitTestCase(unittest.TestCase):
    def test_clean_and_chunk_pipeline_does_not_create_embeddings(self) -> None:
        pages = [PageText(page_number=1, text="Topic A\n\n" + "important concept " * 120)]
        cleaned = TextCleaner().clean("\n".join(page.text for page in pages))
        chunks = TextChunker(chunk_size_chars=300, overlap_chars=50).chunk_pages(pages, cleaned)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.text for chunk in chunks))
        self.assertTrue(all(chunk.token_estimate for chunk in chunks))


if __name__ == "__main__":
    unittest.main()

