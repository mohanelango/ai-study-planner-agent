from dataclasses import dataclass

import fitz

from app.infrastructure.document_processing.exceptions import DocumentExtractionError, EmptyDocumentError


@dataclass(frozen=True)
class PageText:
    page_number: int
    text: str


class PDFTextExtractor:
    def extract_pages(self, pdf_bytes: bytes) -> list[PageText]:
        try:
            document = fitz.open(stream=pdf_bytes, filetype="pdf")
        except Exception as exc:
            raise DocumentExtractionError("PDF could not be opened") from exc

        try:
            if document.needs_pass:
                raise DocumentExtractionError("Encrypted PDFs are not supported")
            pages = [PageText(page_number=index + 1, text=page.get_text("text") or "") for index, page in enumerate(document)]
        except DocumentExtractionError:
            raise
        except Exception as exc:
            raise DocumentExtractionError() from exc
        finally:
            document.close()

        if not any(page.text.strip() for page in pages):
            raise EmptyDocumentError()
        return pages

