"""
Clinical document chunker.
Splits clinical documents into coherent semantic chunks preserving section headers.
"""

import re
from typing import List, Dict, Any


class DocumentChunker:
    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, text: str) -> List[Dict[str, Any]]:
        """
        Split document text into structured chunks with section detection.
        """
        if not text or not text.strip():
            return []

        # Split into sections based on markdown headers or uppercase labels
        section_pattern = r"(?:^|\n)(#{1,4}\s+[^\n]+|[A-Z\s]{4,30}:)"
        parts = re.split(section_pattern, text)

        chunks_data: List[Dict[str, Any]] = []
        current_section = "Introduction / Overview"
        chunk_idx = 0

        i = 0
        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue

            # Check if this part is a section header
            if re.match(r"^#{1,4}\s+", part) or (re.match(r"^[A-Z\s]{4,30}:$", part) and len(part) < 35):
                current_section = part.lstrip("#").strip().rstrip(":")
                i += 1
                if i < len(parts):
                    section_body = parts[i].strip()
                    sub_chunks = self._split_text_into_chunks(section_body)
                    for sc in sub_chunks:
                        chunks_data.append({
                            "chunk_index": chunk_idx,
                            "section": current_section,
                            "content": f"[{current_section}] {sc}",
                        })
                        chunk_idx += 1
                i += 1
            else:
                sub_chunks = self._split_text_into_chunks(part)
                for sc in sub_chunks:
                    chunks_data.append({
                        "chunk_index": chunk_idx,
                        "section": current_section,
                        "content": sc,
                    })
                    chunk_idx += 1
                i += 1

        # Fallback if no structured sections were extracted
        if not chunks_data:
            sub_chunks = self._split_text_into_chunks(text)
            for idx, sc in enumerate(sub_chunks):
                chunks_data.append({
                    "chunk_index": idx,
                    "section": "General",
                    "content": sc,
                })

        return chunks_data

    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text block into chunks of approximately target_chunk_size words."""
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: List[str] = []
        current_chunk_words: List[str] = []

        for p in paragraphs:
            words = p.split()
            if len(current_chunk_words) + len(words) <= self.target_chunk_size:
                current_chunk_words.extend(words)
            else:
                if current_chunk_words:
                    chunks.append(" ".join(current_chunk_words))
                    # Retain overlap words
                    overlap_words = current_chunk_words[-self.chunk_overlap:] if len(current_chunk_words) > self.chunk_overlap else []
                    current_chunk_words = overlap_words + words
                else:
                    # Single paragraph exceeds chunk size, split by words
                    for start_idx in range(0, len(words), self.target_chunk_size - self.chunk_overlap):
                        chunk_slice = words[start_idx : start_idx + self.target_chunk_size]
                        chunks.append(" ".join(chunk_slice))
                    current_chunk_words = []

        if current_chunk_words:
            chunks.append(" ".join(current_chunk_words))

        return chunks


document_chunker = DocumentChunker()
