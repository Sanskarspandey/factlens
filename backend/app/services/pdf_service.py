"""PDF processing and visual grounding service using PyMuPDF (fitz)."""
import hashlib
import os
import re
from typing import List, Dict, Any, Optional, Tuple
import pymupdf as fitz
from app.core.exceptions import InvalidPDFError, DocumentProcessingError
from app.core.logging import logger


class PDFService:
    """Extracts text, layout blocks, metadata, and coordinates from arbitrary PDFs."""

    @staticmethod
    def calculate_file_hash(file_bytes: bytes) -> str:
        """Computes SHA-256 hash for document deduplication and integrity."""
        return hashlib.sha256(file_bytes).hexdigest()

    def validate_pdf(self, file_path: str) -> Tuple[bool, int, str]:
        """
        Validates if file exists and is a readable, non-empty PDF.
        Returns: (is_valid, num_pages, error_message)
        """
        if not os.path.exists(file_path):
            return False, 0, f"File not found: {file_path}"

        try:
            doc = fitz.open(file_path)
            num_pages = len(doc)
            if num_pages == 0:
                doc.close()
                return False, 0, "PDF contains zero pages."
            doc.close()
            return True, num_pages, ""
        except Exception as e:
            return False, 0, f"Invalid or corrupted PDF: {str(e)}"

    def extract_pages(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses all pages in the PDF into structured text blocks and layout metadata.
        Returns a list of page objects with 1-indexed page_numbers.
        """
        is_valid, num_pages, err = self.validate_pdf(file_path)
        if not is_valid:
            raise InvalidPDFError(f"Cannot extract pages from invalid PDF: {err}")

        pages_data = []
        try:
            doc = fitz.open(file_path)
            for page_idx in range(len(doc)):
                page = doc[page_idx]
                page_num = page_idx + 1  # 1-indexed
                raw_text = page.get_text("text")
                
                # Extract layout blocks: (x0, y0, x1, y1, text, block_no, block_type)
                raw_blocks = page.get_text("blocks")
                layout_blocks = []
                for b in raw_blocks:
                    if len(b) >= 6:
                        layout_blocks.append({
                            "bbox": [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)],
                            "text": b[4].strip(),
                            "block_no": b[5],
                            "block_type": b[6] if len(b) > 6 else 0
                        })

                page_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
                rect = page.rect

                pages_data.append({
                    "page_number": page_num,
                    "raw_text": raw_text,
                    "layout_blocks": layout_blocks,
                    "page_hash": page_hash,
                    "width": round(rect.width, 2),
                    "height": round(rect.height, 2)
                })

            doc.close()
            return pages_data
        except Exception as e:
            logger.error(f"Error extracting pages from PDF {file_path}: {e}")
            raise DocumentProcessingError(f"Failed extracting PDF pages: {str(e)}")

    def find_quote_bounding_box(self, file_path: str, page_number: int, quote: str) -> Optional[List[float]]:
        """
        Finds exact or best-matching bounding box [x0, y0, x1, y1] for an evidence quote on a page.
        """
        if not os.path.exists(file_path) or not quote or not quote.strip():
            return None

        clean_quote = quote.strip()
        try:
            doc = fitz.open(file_path)
            if page_number < 1 or page_number > len(doc):
                doc.close()
                return None

            page = doc[page_number - 1]  # 0-indexed

            # 1. Try exact search
            rects = page.search_for(clean_quote)
            if rects:
                r = rects[0]
                doc.close()
                return [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]

            # 2. Try single-spaced search (if quote had line breaks in PDF)
            collapsed_quote = " ".join(clean_quote.split())
            rects = page.search_for(collapsed_quote)
            if rects:
                r = rects[0]
                doc.close()
                return [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]

            # 3. Try leading sentence fragment (first 5-7 words)
            words = clean_quote.split()
            if len(words) >= 4:
                prefix = " ".join(words[:min(6, len(words))])
                rects = page.search_for(prefix)
                if rects:
                    r = rects[0]
                    doc.close()
                    return [round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)]

            # 4. Search within layout blocks
            blocks = page.get_text("blocks")
            for b in blocks:
                if len(b) >= 5 and clean_quote in b[4]:
                    doc.close()
                    return [round(b[0], 2), round(b[1], 2), round(b[2], 2), round(b[3], 2)]

            doc.close()
            return None
        except Exception as e:
            logger.warning(f"Failed calculating bounding box for quote on page {page_number}: {e}")
            return None
