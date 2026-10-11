from __future__ import annotations
import re
from typing import List, Dict, Any
from app.config import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS


class EvidenceChunkData:
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        index: int,
        text: str,
        start_char: int,
        end_char: int,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.index = index
        self.text = text
        self.start_char = start_char
        self.end_char = end_char
        self.char_count = len(text)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "index": self.index,
            "text": self.text,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "char_count": self.char_count,
        }


def chunk_document(
    document_id: str,
    text: str,
    chunk_size: int = CHUNK_SIZE_CHARS,
    overlap: int = CHUNK_OVERLAP_CHARS,
) -> List[EvidenceChunkData]:
    """
    Split text into overlapping chunks respecting paragraph and line boundaries.
    Preserves exact character offsets and deterministic chunk IDs.
    """
    chunks: List[EvidenceChunkData] = []
    text_length = len(text)
    if text_length == 0:
        return chunks

    # If text is smaller than chunk size, return single chunk
    if text_length <= chunk_size:
        return [
            EvidenceChunkData(
                chunk_id=f"chunk-{document_id}-0",
                document_id=document_id,
                index=0,
                text=text.strip(),
                start_char=0,
                end_char=text_length,
            )
        ]

    start = 0
    chunk_index = 0

    while start < text_length:
        end = min(start + chunk_size, text_length)

        # If not at the very end of the text, look for natural split boundaries
        if end < text_length:
            # Look backwards from 'end' for paragraph breaks or sentence ends
            window = text[max(start, end - 120):end]
            para_break = window.rfind("\n\n")
            if para_break != -1:
                end = max(start, end - 120) + para_break + 2
            else:
                line_break = window.rfind("\n")
                if line_break != -1:
                    end = max(start, end - 120) + line_break + 1
                else:
                    sentence_break = re.search(r"[.!?]\s", window)
                    if sentence_break:
                        last_idx = 0
                        for m in re.finditer(r"[.!?]\s", window):
                            last_idx = m.end()
                        if last_idx > 0:
                            end = max(start, end - 120) + last_idx

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append(
                EvidenceChunkData(
                    chunk_id=f"chunk-{document_id}-{chunk_index}",
                    document_id=document_id,
                    index=chunk_index,
                    text=chunk_text,
                    start_char=start,
                    end_char=end,
                )
            )
            chunk_index += 1

        if end >= text_length:
            break

        start = max(start + 1, end - overlap)

    return chunks
