from dataclasses import dataclass

from app.infrastructure.document_processing.pdf_extractor import PageText


@dataclass(frozen=True)
class TextChunk:
    chunk_index: int
    text: str
    page_start: int | None
    page_end: int | None
    char_start: int
    char_end: int
    token_estimate: int


class TextChunker:
    def __init__(self, chunk_size_chars: int = 1200, overlap_chars: int = 150) -> None:
        if overlap_chars >= chunk_size_chars:
            raise ValueError("overlap_chars must be smaller than chunk_size_chars")
        self.chunk_size_chars = chunk_size_chars
        self.overlap_chars = overlap_chars

    def chunk_pages(self, pages: list[PageText], cleaned_text: str) -> list[TextChunk]:
        if not cleaned_text:
            return []
        page_ranges = self._page_ranges(pages)
        chunks: list[TextChunk] = []
        start = 0
        while start < len(cleaned_text):
            end = min(start + self.chunk_size_chars, len(cleaned_text))
            chunk_text = cleaned_text[start:end].strip()
            if chunk_text:
                page_start, page_end = self._pages_for_range(page_ranges, start, end)
                chunks.append(
                    TextChunk(
                        chunk_index=len(chunks),
                        text=chunk_text,
                        page_start=page_start,
                        page_end=page_end,
                        char_start=start,
                        char_end=end,
                        token_estimate=max(1, len(chunk_text) // 4),
                    )
                )
            if end >= len(cleaned_text):
                break
            start = max(0, end - self.overlap_chars)
        return chunks

    @staticmethod
    def _page_ranges(pages: list[PageText]) -> list[tuple[int, int, int]]:
        ranges: list[tuple[int, int, int]] = []
        cursor = 0
        for page in pages:
            text_length = len(page.text.strip())
            ranges.append((page.page_number, cursor, cursor + text_length))
            cursor += text_length + 1
        return ranges

    @staticmethod
    def _pages_for_range(page_ranges: list[tuple[int, int, int]], start: int, end: int) -> tuple[int | None, int | None]:
        matched = [page_number for page_number, page_start, page_end in page_ranges if page_end >= start and page_start <= end]
        if not matched:
            return None, None
        return min(matched), max(matched)

