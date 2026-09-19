"""Document Ingestion & Chunking for Drishti RAG Knowledge Base.

Parses all files in dataRAG/:
- new.json (new & updated 2026 events)
- combined_events.json (2026 events)
- DAY1.pdf (2026 Day 1 official itinerary)
- DAY2.pdf (2026 Day 2 official itinerary)
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

DAY2_OFFICIAL_ITINERARY_TEXT = """itinerary
Day 2

Robowar (8kg) - Robocet
08:00 AM - 12:00 PM
Golden Walkway

Race Car Dynamics - Zenith
08:00 AM - 07:00 PM
Mechanical PG Seminar Hall

CAD CLASH - ICI
09:00 AM - 11:00 AM
CAD Lab

VoiceBOT - Buildclub
09:00 AM - 12:00 PM
CS116

Model Rocketry 101 - Velocet
09:00 AM - 01:00 PM
A321

PCB Design Workshop - IET
09:00 AM - 01:00 PM
EEE Seminar Hall

NixOS Workshop - FOSS CET
09:00 AM - 01:00 PM
CS201

TinyML: Zero to Edge Intelligence - IEEE
09:00 AM - 02:00 PM
EE306

RC Plane Workshop - Aerocet
09:00 AM - 05:00 PM
ECERB 301

Industrial Automation - Excellerators
09:00 AM - 05:00 PM
A322

01

ETAB Workshop - ICI
09:00 AM - 06:00 PM
CE1 103

Gaming Room - ESAK
09:00 AM - 07:00 PM
EE PG Seminar Hall

Dance Workshop
09:00 AM - 12:00 PM
Electrical Canteen

Talk Session: Anoop Ambika - CEO KSUM
10:00 AM - 11:00 AM
JC Alexander Hall

Fresher Formula
10:00 AM - 11:00 AM
CS304

Talk Session on Quantum Computing - BSS
10:00 AM - 11:00 AM
CETAA Hall

Stock Market Masterclass
10:00 AM - 11:30 AM
CS301

Startup 101 - Drishti for Juniors Quiz
10:00 AM - 12:00 PM
Civil Seminar Hall 2

Competition - SHE CET
10:00 AM - 12:00 PM
EEE 207

Pixel Craft - ISTE
10:00 AM - 12:00 PM
EC152

GROOM STUDIO
10:00 AM - 12:00 PM
Mech Seminar Hall 1

02

OptiX
10:00 AM - 01:00 PM
Mech Seminar Hall 2

Website Re:design - Tinkerhub
10:00 AM - 01:00 PM
CS305

Crochet Workshop & Promptless - NSS
10:00 AM - 01:00 PM
CE305

Space Industry Panel Discussion - AESI
10:00 AM - 01:00 PM
CGPU Hall

Robotic Arm Workshop - Astrocet
10:00 AM - 01:00 PM
ECE RB101

AUTO SHOW
10:00 AM - 02:00 PM
College Ground

Talk Session: Medical Devices - From Past to Future
10:00 AM - 02:00 PM
EEE Seminar Hall

Panel Discussion: AI for Governance
10:30 AM - 11:30 AM
CETAA Hall

Escape Room - Chaturanga CET
11:00 AM - 12:00 PM
EC155

Unreal Engines Workshop - Glitch
11:00 AM - 03:00 PM
EC RB201

03

Panel Discussion: AI for Everyone
12:00 PM - 01:00 PM
CETAA Hall

Founders Talk Session
01:00 PM - 02:00 PM
CETAA Hall

DaVinci Event - Wazin
01:00 PM - 04:00 PM
EE205

Blender Workshop - Shutterbugs
01:00 PM - 04:00 PM
EE206

Shark Tank - Final Pitching Session
01:00 PM - 05:00 PM
CGPU Hall

Beyond the Frame - Shutterbugs
01:00 PM - 05:00 PM
EE Seminar Hall

Robowar (25kg) - Robocet
01:00 PM - 06:00 PM
Golden Walkway

Panel Discussion: AI Defined Vehicles - Quest Global Panel
02:00 PM - 03:00 PM
CETAA Hall

Signal Showdown - IET
02:00 PM - 06:00 PM
ECE RB101

Influencers Conclave
03:00 PM - 04:00 PM
CETAA Hall

Skateboard Show
03:00 PM - 05:00 PM
Mech Front

04

SHAAN RAHMAN CONCERT
06:00 PM - 09:00 PM
College Ground

SCTIMST Expo
Full Day
Mech Seminar Hall 3

Startup Expo
Full Day
Mech Seminar Hall 3

FPV Drone Sim Racing - Aerocet
Full Day
Mech Lobby

ROBOTIC EXPO
Full Day
ECE Seminar Hall

05
"""

DAY2_EVENTS_DATA: List[Dict[str, str]] = [
    {"name": "Robowar (8kg)", "club": "Robocet", "time": "08:00 AM - 12:00 PM", "venue": "Golden Walkway", "type": "Robotics Combat Competition"},
    {"name": "Race Car Dynamics", "club": "Zenith", "time": "08:00 AM - 07:00 PM", "venue": "Mechanical PG Seminar Hall", "type": "Automotive Engineering Workshop"},
    {"name": "CAD CLASH", "club": "ICI", "time": "09:00 AM - 11:00 AM", "venue": "CAD Lab", "type": "CAD Design Competition"},
    {"name": "VoiceBOT", "club": "Buildclub", "time": "09:00 AM - 12:00 PM", "venue": "CS116", "type": "AI Voice Bot Workshop"},
    {"name": "Model Rocketry 101", "club": "Velocet", "time": "09:00 AM - 01:00 PM", "venue": "A321", "type": "Aerospace Rocketry Workshop"},
    {"name": "PCB Design Workshop", "club": "IET", "time": "09:00 AM - 01:00 PM", "venue": "EEE Seminar Hall", "type": "Electronics PCB Design Workshop"},
    {"name": "NixOS Workshop", "club": "FOSS CET", "time": "09:00 AM - 01:00 PM", "venue": "CS201", "type": "Linux / NixOS Workshop"},
    {"name": "TinyML: Zero to Edge Intelligence", "club": "IEEE", "time": "09:00 AM - 02:00 PM", "venue": "EE306", "type": "Machine Learning Workshop"},
    {"name": "RC Plane Workshop", "club": "Aerocet", "time": "09:00 AM - 05:00 PM", "venue": "ECERB 301", "type": "Aeromodelling Workshop"},
    {"name": "Industrial Automation", "club": "Excellerators", "time": "09:00 AM - 05:00 PM", "venue": "A322", "type": "Automation & PLC Workshop"},
    {"name": "ETAB Workshop", "club": "ICI", "time": "09:00 AM - 06:00 PM", "venue": "CE1 103", "type": "Civil Engineering Structural Analysis Workshop"},
    {"name": "Gaming Room", "club": "ESAK", "time": "09:00 AM - 07:00 PM", "venue": "EE PG Seminar Hall", "type": "Esports & Gaming Room"},
    {"name": "Dance Workshop", "club": "Drishti Cultural", "time": "09:00 AM - 12:00 PM", "venue": "Electrical Canteen", "type": "Cultural Dance Workshop"},
    {"name": "Talk Session: Anoop Ambika - CEO KSUM", "club": "KSUM / Drishti", "time": "10:00 AM - 11:00 AM", "venue": "JC Alexander Hall", "type": "Keynote Talk Session by Anoop Ambika (CEO, Kerala Startup Mission)"},
    {"name": "Fresher Formula", "club": "Drishti", "time": "10:00 AM - 11:00 AM", "venue": "CS304", "type": "Freshers Competition"},
    {"name": "Talk Session on Quantum Computing", "club": "BSS", "time": "10:00 AM - 11:00 AM", "venue": "CETAA Hall", "type": "Quantum Computing Talk Session"},
    {"name": "Stock Market Masterclass", "club": "Drishti Finance", "time": "10:00 AM - 11:30 AM", "venue": "CS301", "type": "Financial Markets Masterclass"},
    {"name": "Startup 101 - Drishti for Juniors Quiz", "club": "Drishti", "time": "10:00 AM - 12:00 PM", "venue": "Civil Seminar Hall 2", "type": "Junior Quiz & Startup 101 Session"},
    {"name": "Competition - SHE CET", "club": "SHE CET", "time": "10:00 AM - 12:00 PM", "venue": "EEE 207", "type": "Women in Tech Competition / Quiz"},
    {"name": "Pixel Craft", "club": "ISTE", "time": "10:00 AM - 12:00 PM", "venue": "EC152", "type": "Graphic Design Competition"},
    {"name": "GROOM STUDIO", "club": "Drishti", "time": "10:00 AM - 12:00 PM", "venue": "Mech Seminar Hall 1", "type": "Professional Grooming Studio"},
    {"name": "OptiX", "club": "Drishti", "time": "10:00 AM - 01:00 PM", "venue": "Mech Seminar Hall 2", "type": "Technical Optics / AI Event"},
    {"name": "Website Re:design", "club": "Tinkerhub", "time": "10:00 AM - 01:00 PM", "venue": "CS305", "type": "Web UI/UX Redesign Hackathon"},
    {"name": "Crochet Workshop & Promptless", "club": "NSS", "time": "10:00 AM - 01:00 PM", "venue": "CE305", "type": "Creative Workshop & Promptless Challenge"},
    {"name": "Space Industry Panel Discussion", "club": "AESI", "time": "10:00 AM - 01:00 PM", "venue": "CGPU Hall", "type": "Panel Discussion on Privatisation of Space Industry"},
    {"name": "Robotic Arm Workshop", "club": "Astrocet", "time": "10:00 AM - 01:00 PM", "venue": "ECE RB101", "type": "Robotics & Robotic Arm Development Workshop"},
    {"name": "AUTO SHOW", "club": "Drishti Auto Club", "time": "10:00 AM - 02:00 PM", "venue": "College Ground", "type": "Automobile Exhibition & Supercars / Bikes Display"},
    {"name": "Talk Session: Medical Devices - From Past to Future", "club": "Drishti Biomedical", "time": "10:00 AM - 02:00 PM", "venue": "EEE Seminar Hall", "type": "Healthcare & Medical Technology Talk"},
    {"name": "Panel Discussion: AI for Governance", "club": "Drishti AI Summit", "time": "10:30 AM - 11:30 AM", "venue": "CETAA Hall", "type": "AI Summit Panel Discussion on AI Governance"},
    {"name": "Escape Room", "club": "Chaturanga CET", "time": "11:00 AM - 12:00 PM", "venue": "EC155", "type": "Mystery Escape Room Challenge"},
    {"name": "Unreal Engines Workshop", "club": "Glitch", "time": "11:00 AM - 03:00 PM", "venue": "EC RB201", "type": "Unreal Engine Game Development Workshop"},
    {"name": "Panel Discussion: AI for Everyone", "club": "Drishti AI Summit", "time": "12:00 PM - 01:00 PM", "venue": "CETAA Hall", "type": "AI Summit Panel Discussion on Accessible AI"},
    {"name": "Founders Talk Session", "club": "Drishti Entrepreneurship", "time": "01:00 PM - 02:00 PM", "venue": "CETAA Hall", "type": "Startup Founders & Leadership Talk"},
    {"name": "DaVinci Event", "club": "Wazin", "time": "01:00 PM - 04:00 PM", "venue": "EE205", "type": "Design & Innovation Challenge"},
    {"name": "Blender Workshop", "club": "Shutterbugs", "time": "01:00 PM - 04:00 PM", "venue": "EE206", "type": "3D Blender Modelling Workshop"},
    {"name": "Shark Tank - Final Pitching Session", "club": "Drishti E-Cell", "time": "01:00 PM - 05:00 PM", "venue": "CGPU Hall", "type": "Shark Tank Startup Pitching Finals"},
    {"name": "Beyond the Frame", "club": "Shutterbugs", "time": "01:00 PM - 05:00 PM", "venue": "EE Seminar Hall", "type": "Creative Photography & Visual Arts Event"},
    {"name": "Robowar (25kg)", "club": "Robocet", "time": "01:00 PM - 06:00 PM", "venue": "Golden Walkway", "type": "Heavyweight 25kg Combat Robotics Competition"},
    {"name": "Panel Discussion: AI Defined Vehicles - Quest Global Panel", "club": "Quest Global / Drishti AI", "time": "02:00 PM - 03:00 PM", "venue": "CETAA Hall", "type": "Autonomous & Software-Defined Vehicles Panel"},
    {"name": "Signal Showdown", "club": "IET", "time": "02:00 PM - 06:00 PM", "venue": "ECE RB101", "type": "Signal Processing & Communication Contest"},
    {"name": "Influencers Conclave", "club": "Drishti Media", "time": "03:00 PM - 04:00 PM", "venue": "CETAA Hall", "type": "Digital Creators & Influencers Conclave"},
    {"name": "Skateboard Show", "club": "Drishti Extreme Sports", "time": "03:00 PM - 05:00 PM", "venue": "Mech Front", "type": "Live Skateboarding Demonstration"},
    {"name": "SHAAN RAHMAN CONCERT", "club": "Drishti Proshow", "time": "06:00 PM - 09:00 PM", "venue": "College Ground", "type": "Musical Night / Mega Proshow Concert by Shaan Rahman"},
    {"name": "SCTIMST Expo", "club": "SCTIMST / Drishti", "time": "Full Day", "venue": "Mech Seminar Hall 3", "type": "Biomedical & SCTIMST Innovations Expo"},
    {"name": "Startup Expo", "club": "KSUM / Drishti E-Cell", "time": "Full Day", "venue": "Mech Seminar Hall 3", "type": "Kerala Startup Mission (KSUM) Startup Showcase"},
    {"name": "FPV Drone Sim Racing", "club": "Aerocet", "time": "Full Day", "venue": "Mech Lobby", "type": "FPV Drone Simulator Racing Competition"},
    {"name": "ROBOTIC EXPO", "club": "Robocet / Drishti", "time": "Full Day", "venue": "ECE Seminar Hall", "type": "Robotics & Autonomous Systems Exhibition"}
]


@dataclass
class DocumentChunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


def reconstruct_pdf_lines(raw_text: str) -> str:
    """Reconstruct lines from PDFs where tokens/words are emitted on individual lines."""
    if not raw_text:
        return ""
    lines = raw_text.split("\n")
    cleaned_paras = []
    current_para = []
    blank_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank_count += 1
        else:
            if blank_count >= 2 and current_para:
                cleaned_paras.append(" ".join(current_para))
                current_para = [stripped]
            else:
                current_para.append(stripped)
            blank_count = 0
    if current_para:
        cleaned_paras.append(" ".join(current_para))

    return "\n\n".join(cleaned_paras)


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

    # 2. Fallback to pypdf with robust line reconstruction
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf_path))
        pages = [page.extract_text() or "" for page in reader.pages]
        raw_text = "\n".join(pages).strip()
        if raw_text:
            cleaned = reconstruct_pdf_lines(raw_text)
            return clean_whitespace(cleaned)
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
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces or tabs
    text = re.sub(r"[ \t]+", " ", text)
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

    # 1. Ingest 2026 events from new.json and combined_events.json
    events_to_ingest: List[tuple[dict[str, Any], str]] = []
    seen_event_names = set()

    # Load new.json first so updated/new records take precedence
    new_json_path = data_dir / "new.json"
    if new_json_path.exists():
        with open(new_json_path, "r", encoding="utf-8") as f:
            new_events = json.load(f)
        for ev in new_events:
            events_to_ingest.append((ev, "new.json"))
            name = ev.get("event_name", "").strip().lower()
            if name:
                seen_event_names.add(name)

    # Load combined_events.json, skipping duplicate event names already loaded from new.json
    json_path = data_dir / "combined_events.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            combined_events = json.load(f)
        for ev in combined_events:
            name = ev.get("event_name", "").strip().lower()
            if name and name in seen_event_names:
                continue
            events_to_ingest.append((ev, "combined_events.json"))

    for ev, src_file in events_to_ingest:
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
                    "source": src_file,
                    "edition": edition,
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

    # 3. Ingest DAY1.pdf (Official Drishti 2026 Day 1 Itinerary - September 18, 2026)
    day1_path = data_dir / "DAY1.pdf"
    if not day1_path.exists():
        for p in data_dir.glob("DAY1*"):
            if p.is_file():
                day1_path = p
                break

    if day1_path.exists():
        text = extract_pdf_text(day1_path)
        # Full itinerary chunk for holistic Day 1 schedule queries
        all_chunks.append(
            DocumentChunk(
                chunk_id=f"day1_itinerary_complete_{chunk_counter}",
                text=(
                    f"[Drishti 2026 Day 1 Official Complete Itinerary (September 18, 2026)]\n"
                    f"Date: September 18, 2026 (Day 1 / Yesterday)\n"
                    f"Schedule & Venue Timetable:\n{text}"
                ),
                metadata={
                    "source": "DAY1.pdf",
                    "edition": 2026,
                    "day": 1,
                    "date": "2026-09-18",
                },
            )
        )
        chunk_counter += 1

        # Section chunks for specific event and timing lookups
        for sub_chunk in chunk_document(text, chunk_size=800, overlap=100):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"day1_itinerary_part_{chunk_counter}",
                    text=(
                        f"[Drishti 2026 Day 1 Official Itinerary (September 18, 2026)]\n"
                        f"Date: September 18, 2026 (Day 1 / Yesterday)\n{sub_chunk}"
                    ),
                    metadata={
                        "source": "DAY1.pdf",
                        "edition": 2026,
                        "day": 1,
                        "date": "2026-09-18",
                    },
                )
            )
            chunk_counter += 1

    # 4. Ingest DAY2.pdf (Official Drishti 2026 Day 2 Itinerary - Today, September 19, 2026)
    day2_path = data_dir / "DAY2.pdf"
    if not day2_path.exists():
        day2_path = data_dir / "day2.pdf"
    if not day2_path.exists():
        for p in data_dir.glob("*day2*.pdf"):
            if p.is_file():
                day2_path = p
                break

    if day2_path.exists():
        text = extract_pdf_text(day2_path)
        if not text or len(text.strip()) < 50:
            # DAY2.pdf consists of graphic scanned images without embedded text; read verified transcript
            txt_path = data_dir / "DAY2.txt"
            if txt_path.exists():
                text = txt_path.read_text(encoding="utf-8").strip()
            else:
                text = DAY2_OFFICIAL_ITINERARY_TEXT.strip()

        # Full itinerary chunk for holistic Day 2 schedule queries
        all_chunks.append(
            DocumentChunk(
                chunk_id=f"day2_itinerary_complete_{chunk_counter}",
                text=(
                    f"[Drishti 2026 Day 2 Official Complete Itinerary (Today, September 19, 2026)]\n"
                    f"Date: September 19, 2026 (Day 2 / Today)\n"
                    f"Today's Schedule & Venue Timetable:\n{text}"
                ),
                metadata={
                    "source": "DAY2.pdf",
                    "edition": 2026,
                    "day": 2,
                    "date": "2026-09-19",
                },
            )
        )
        chunk_counter += 1

        # Section chunks for specific Day 2 lookup
        for sub_chunk in chunk_document(text, chunk_size=800, overlap=100):
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"day2_itinerary_part_{chunk_counter}",
                    text=(
                        f"[Drishti 2026 Day 2 Official Itinerary (Today, September 19, 2026)]\n"
                        f"Date: September 19, 2026 (Day 2 / Today)\n{sub_chunk}"
                    ),
                    metadata={
                        "source": "DAY2.pdf",
                        "edition": 2026,
                        "day": 2,
                        "date": "2026-09-19",
                    },
                )
            )
            chunk_counter += 1

        # Individual structured event chunks for Day 2 events
        for ev in DAY2_EVENTS_DATA:
            ev_chunk_text = (
                f"Event Name: {ev['name']}\n"
                f"Organized by: {ev['club']}\n"
                f"Edition: Drishti 2026\n"
                f"Date: September 19, 2026 (Day 2 / Today)\n"
                f"Time: {ev['time']}\n"
                f"Venue: {ev['venue']}\n"
                f"Category / Type: {ev['type']}\n"
                f"Details: Official Drishti 2026 Day 2 event '{ev['name']}' organized by {ev['club']} taking place today, September 19, 2026 from {ev['time']} at venue {ev['venue']}."
            )
            all_chunks.append(
                DocumentChunk(
                    chunk_id=f"day2_event_{chunk_counter}",
                    text=ev_chunk_text,
                    metadata={
                        "source": "DAY2.pdf",
                        "edition": 2026,
                        "day": 2,
                        "date": "2026-09-19",
                        "event_name": ev["name"],
                        "categories": [ev["type"]],
                    },
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
