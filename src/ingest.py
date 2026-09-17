"""Document Ingestion & Chunking for Drishti RAG Knowledge Base.

Parses all files in dataRAG/:
- combined_events.json (2026 events)
- Drishti-26.pdf (2026 overview & schedule)
- ai_summit_data.pdf (2026 AI Summit)
- Drishti'24.docx.pdf (2024 historical archive)
- drishti2022.docx (2022 historical archive)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent.parent / "dataRAG"


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from PDF using pdftotext first (clean layout), falling back to pypdf."""
    # 1. Try pdftotext CLI for pristine paragraph formatting
    try:
        result = subprocess.run(
            ["pdftotext", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            check=True,
        )
        text = result.stdout.strip()
        if text:
            return clean_whitespace(text)
    except Exception:
        pass

    # 2. Fallback to pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages).strip()
        if text:
            return clean_whitespace(text)
    except Exception:
        pass

    return ""


def extract_docx_text(docx_path: Path) -> str:
    """Extract text from docx using python-docx if available, falling back to XML."""
    try:
        import docx
        doc = docx.Document(str(docx_path))
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs).strip()
    except Exception:
        pass

    # Direct word/document.xml extraction
    try:
        with zipfile.ZipFile(docx_path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            namespaces = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in tree.findall(".//w:p", namespaces):
                texts = [node.text for node in p.findall(".//w:t", namespaces) if node.text]
                p_text = "".join(texts).strip()
                if p_text:
                    paragraphs.append(p_text)
            return "\n\n".join(paragraphs).strip()
    except Exception:
        return ""


def clean_whitespace(text: str) -> str:
    """Normalize excess newlines and whitespace."""
    # Fix words split by line breaks
    text = re.sub(r"(\b\w+)\n(\w+\b)", r"\1 \2", text)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_document(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """Split clean text into semantic chunks with overlap."""
    if not text:
        return []
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_len = 0

    for p in paras:
        if current_len + len(p) > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p]
            current_len = len(p)
        else:
            current_chunk.append(p)
            current_len += len(p)

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text]


def load_all_chunks(data_dir: Path = DATA_DIR) -> List[DocumentChunk]:
    """Ingest and chunk all data sources in dataRAG/."""
    all_chunks: List[DocumentChunk] = []
    chunk_counter = 0

    # 1. Ingest combined_events.json (2026 events)
    json_path = data_dir / "combined_events.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            events = json.load(f)
        for ev in events:
            name = ev.get("event_name", "Unknown Event")
            edition = ev.get("edition", 2026)
            days = ev.get("days", [])
            dates = ev.get("dates", [])
            categories = ", ".join(ev.get("categories", []))
            source_text = ev.get("source_text", "")
            search_text = ev.get("search_text", "")

            chunk_content = (
                f"Event Name: {name}\n"
                f"Edition: Drishti {edition}\n"
                f"Dates: {', '.join(dates) if dates else 'N/A'} (Days: {', '.join(map(str, days)) if days else 'N/A'})\n"
                f"Categories: {categories}\n"
                f"Details:\n{source_text}\n"
                f"Summary: {search_text}"
            )
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"event_2026_{chunk_counter}",
                    text=chunk_content,
                    metadata={
                        "source": "combined_events.json",
                        "edition": 2026,
                        "event_name": name,
                        "categories": ev.get("categories", []),
                    },
                )
            )
            chunk_counter += 1

    # 2. Ingest Drishti-26.pdf
    d26_path = data_dir / "Drishti-26.pdf"
    if d26_path.exists():
        text = extract_pdf_text(d26_path)
        for sub_chunk in chunk_document(text, chunk_size=800, overlap=100):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"drishti26_pdf_{chunk_counter}",
                    text=f"[Drishti 2026 Overview & Schedule]\n{sub_chunk}",
                    metadata={"source": "Drishti-26.pdf", "edition": 2026},
                )
            )
            chunk_counter += 1

    # 3. Ingest ai_summit_data.pdf
    ai_summit_path = data_dir / "ai_summit_data.pdf"
    if ai_summit_path.exists():
        text = extract_pdf_text(ai_summit_path)
        for sub_chunk in chunk_document(text, chunk_size=800, overlap=100):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"ai_summit_pdf_{chunk_counter}",
                    text=f"[Drishti 2026 AI Summit]\n{sub_chunk}",
                    metadata={"source": "ai_summit_data.pdf", "edition": 2026},
                )
            )
            chunk_counter += 1

    # 4. Ingest Drishti'24.docx.pdf (2024 archive)
    d24_path = data_dir / "Drishti'24.docx.pdf"
    if d24_path.exists():
        text = extract_pdf_text(d24_path)
        for sub_chunk in chunk_document(text, chunk_size=700, overlap=80):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"drishti24_pdf_{chunk_counter}",
                    text=f"[Drishti 2024 Archive Event Details]\n{sub_chunk}",
                    metadata={"source": "Drishti'24.docx.pdf", "edition": 2024},
                )
            )
            chunk_counter += 1

    # 5. Ingest drishti2022.docx (2022 archive)
    d22_path = data_dir / "drishti2022.docx"
    if d22_path.exists():
        text = extract_docx_text(d22_path)
        for sub_chunk in chunk_document(text, chunk_size=700, overlap=80):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"drishti22_docx_{chunk_counter}",
                    text=f"[Drishti 2022 Archive Event Details]\n{sub_chunk}",
                    metadata={"source": "drishti2022.docx", "edition": 2022},
                )
            )
            chunk_counter += 1

    return all_chunks
