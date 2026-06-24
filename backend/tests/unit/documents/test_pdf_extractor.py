import unittest

from app.infrastructure.document_processing.exceptions import DocumentExtractionError
from app.infrastructure.document_processing.pdf_extractor import PDFTextExtractor


class PDFExtractorTestCase(unittest.TestCase):
    def test_unreadable_pdf_fails_cleanly(self) -> None:
        with self.assertRaises(DocumentExtractionError):
            PDFTextExtractor().extract_pages(b"not a pdf")


if __name__ == "__main__":
    unittest.main()

