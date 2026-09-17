import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "clean_data.json"
POSTER_DOCS = ROOT.parent / "posters"
POSTER_INDEX = POSTER_DOCS / "poster_index.json"


def make_record(source_text, event_name=None, day=None, date=None, category=None, organizers=None, poster_path=None):
    text = source_text.strip()
    if not text:
        raise ValueError("empty source text")
    lower = text.lower()
    edition = 2026
    days = []
    if day:
        days = [int(day)]
    dates = []
    if date:
        dates = [date]
    categories = []
    if category:
        categories = [category]
    if re.search(r"panel discussion|panel", lower):
        categories.append("panel")
    if re.search(r"talk session|talk|speaker", lower):
        categories.append("talk")
    if re.search(r"expo|exhibition", lower):
        categories.append("expo")
    if re.search(r"workshop", lower):
        categories.append("workshop")
    if re.search(r"hackathon|summit", lower):
        categories.append("summit")
    categories = sorted(set(categories))
    record = {
        "id": "ai-summit-" + re.sub(r"[^a-z0-9]+", "-", (event_name or text)[:60].lower()).strip("-") or "record",
        "source_text": text,
        "search_text": f"{text} {event_name or ''} {' '.join(categories)} {' '.join(organizers or [])}".strip(),
        "festival": "Drishti",
        "edition": edition,
        "days": days,
        "dates": dates,
        "categories": categories,
        "organizers": sorted(set(organizers or [])),
        "event_name": event_name or text[:120],
        "is_scheduled": bool(days or dates),
        "is_listable": bool(days or dates),
        "kind": "text",
        "poster_path": poster_path,
    }
    return record


WORKSHOP_POSTER_MAP = {
    "sensor fusion 101": "posters/sensorfusion101.jpeg",
    "ansys": "posters/ansys.jpeg",
    "verilog and fpga": "posters/verilogandfgpa.jpeg",
    "opencv": "posters/opencv.jpeg",
    "engine": "posters/engineworkshop.jpeg",
    "8 bit computer": "posters/8bit.jpeg",
    "8-bit computer": "posters/8bit.jpeg",
    "workshop on building an 8 bit computer": "posters/8bit.jpeg",
    "workshop on building an 8-bit computer": "posters/8bit.jpeg",
    "rc plane": "posters/rcplane.jpeg",
    "model rocketry 101": "posters/modelrocketry.jpeg",
    "tinyml": "posters/tinyml.jpeg",
    "escape room": "posters/escaperoom.jpeg",
    "fpv drone sim racing": "posters/dronrace.jpg",
    "ai summit overview": "posters/drishti-2026-ai-summit-overview-poster.png",
    "ai summit day 1 overview": "posters/drishti-2026-ai-summit-day-1-poster.png",
    "women in tech": "posters/drishti-2026-ai-summit-day-1-poster.png",
    "ai in the automotive industry": "posters/drishti-2026-ai-summit-day-1-poster.png",
    "victims of cyber fraud": "posters/drishti-2026-ai-summit-day-1-poster.png",
}


AI_SUMMIT_RECORDS = [
    make_record(
        "The AI Summit is a three-day speaker programme held as part of Drishti 2026, the national techfest of College of Engineering Trivandrum (CET), Kerala. The summit runs from 18 September 2026 to 20 September 2026 and consists of twelve sessions in total: eight panel discussions and four solo talk sessions. Sessions are spread across four venues on the CET campus — the CETAA Hall, the CGPU Hall, the EEE Seminar Hall and the J C Alexander Hall — and run between 10:00 AM and 3:30 PM each day, with some sessions running in parallel at different venues. All speakers listed for the summit have confirmed their participation. Themes across the three days include AI in the automotive industry, AI for governance, AI in healthcare and medical devices, women in technology, the future of work, and questions of access and equity in artificial intelligence. Several sessions are supported by industry partners, most prominently Quest Global, whose automotive vertical team leads four of the panel discussions.",
        event_name="AI Summit Overview",
        day=None,
        date=None,
        category="summit",
        poster_path="posters/drishti-2026-ai-summit-overview-poster.png",
    ),
    make_record(
        "Day 1 of the AI Summit at Drishti 2026 has three sessions. At 12:00 PM the CGPU Hall hosts a panel discussion on women in technology. At 1:30 PM the CETAA Hall hosts a panel discussion on AI in the automotive industry. At 2:30 PM the EEE Seminar Hall hosts a talk session on cyber fraud and the governance of large language models.",
        event_name="AI Summit Day 1 Overview",
        day=1,
        date="2026-09-18",
        category="summit",
        poster_path="posters/drishti-2026-ai-summit-day-1-poster.png",
    ),
    make_record(
        "On 18 September 2026, from 12:00 PM to 1:00 PM at the CGPU Hall, the AI Summit hosts a panel discussion titled 'Women in Tech: Building Tech Where Everyone Belongs.' The panel brings together three confirmed speakers. Jeevadas K Y is a Manager for the Semiconductor Account at Quest Global. Mariyam Vidhu Vijayan is the CEO and Co-Founder of Crink. Dr Aswathy Udayan is Vice President at Equipo Health and holds a PhD and an MBA. The point of contact for this session is Aiveen.",
        event_name="Women in Tech: Building Tech Where Everyone Belongs",
        day=1,
        date="2026-09-18",
        category="panel",
        organizers=["Quest Global", "Crink", "Equipo Health"],
        poster_path="posters/drishti-2026-ai-summit-day-1-poster.png",
    ),
    make_record(
        "On 18 September 2026, from 1:30 PM to 2:30 PM at the CETAA Hall, the AI Summit hosts a panel discussion on AI in the automotive industry. Two confirmed speakers take part. Tony Thomas is a Board Director at EQT, and the point of contact coordinating his participation is Aiveen. Dr Shivoh Chirayil Nandakumar is the CEO and Founder of RideScan, and the point of contact coordinating his participation is Devika Sajeesh.",
        event_name="AI in the Automotive Industry",
        day=1,
        date="2026-09-18",
        category="panel",
        organizers=["EQT", "RideScan"],
        poster_path="posters/drishti-2026-ai-summit-day-1-poster.png",
    ),
    make_record(
        "On 18 September 2026, from 2:30 PM to 3:30 PM at the EEE Seminar Hall, the AI Summit hosts a solo talk session titled 'Victims of Cyber Fraud: Governance Against LLMs.' The speaker is Advocate Jince T Thomas, a cyber lawyer, and his participation is confirmed. The point of contact for this session is Akshay V Sarma.",
        event_name="Victims of Cyber Fraud: Governance Against LLMs",
        day=1,
        date="2026-09-18",
        category="talk",
        organizers=["Advocate Jince T Thomas"],
        poster_path="posters/drishti-2026-ai-summit-day-1-poster.png",
    ),
    make_record(
        "Day 2 of the AI Summit at Drishti 2026 has five sessions. At 10:00 AM the J C Alexander Hall hosts a talk by the CEO of Kerala Startup Mission. At 10:30 AM the EEE Seminar Hall hosts a talk on medical devices. At 11:00 AM the CGPU Hall hosts a panel on AI for governance. At 12:00 PM the CETAA Hall hosts a panel on access and equity in AI. At 2:00 PM the CETAA Hall hosts a panel on AI-defined vehicles.",
        event_name="AI Summit Day 2 Overview",
        day=2,
        date="2026-09-19",
        category="summit",
    ),
    make_record(
        "On 19 September 2026, from 10:00 AM to 11:00 AM at the J C Alexander Hall, the AI Summit hosts a solo talk session by Anoop Ambika, the Chief Executive Officer of Kerala Startup Mission. His participation is confirmed, and the topic of the talk has not yet been finalised. The point of contact for this session is Gautam.",
        event_name="Anoop Ambika talk",
        day=2,
        date="2026-09-19",
        category="talk",
        organizers=["Kerala Startup Mission"],
    ),
    make_record(
        "On 19 September 2026, from 10:30 AM to 11:30 AM at the EEE Seminar Hall, the AI Summit hosts a solo talk session titled 'Medical Devices: From Past to Future — The Global Journey and India's Position.' The speaker is Anoop Gopinath, a Scientist at the Sree Chitra Tirunal Institute for Medical Sciences and Technology (SCTIMST), and his participation is confirmed. The point of contact for this session is Aiveen.",
        event_name="Medical Devices: From Past to Future",
        day=2,
        date="2026-09-19",
        category="talk",
        organizers=["SCTIMST"],
    ),
    make_record(
        "On 19 September 2026, from 11:00 AM to 12:00 PM at the CGPU Hall, the AI Summit hosts a panel discussion on AI for governance. Two confirmed speakers take part. Dr Sabarish Karunakaran is Head of e-Governance at the Kerala State IT Mission (KSITM), and the point of contact coordinating his participation is Avaneesh. Ankit Asokan IPS is a Superintendent of Police with the Kerala Police Cyberdome, and the point of contact coordinating his participation is Abhimanyu.",
        event_name="AI for Governance",
        day=2,
        date="2026-09-19",
        category="panel",
        organizers=["Kerala State IT Mission", "Kerala Police Cyberdome"],
    ),
    make_record(
        "On 19 September 2026, from 12:00 PM to 1:00 PM at the CETAA Hall, the AI Summit hosts a panel discussion titled 'AI for Everyone: Who Gets to Be Intelligent?' Two confirmed speakers take part, both from Cymonic. Sreejith Vadakara is Chief Technology Officer at Cymonic, and Akhil Pulikkal Nandakumar is an AI Architect at Cymonic. The point of contact for this session is Aiveen.",
        event_name="AI for Everyone: Who Gets to Be Intelligent?",
        day=2,
        date="2026-09-19",
        category="panel",
        organizers=["Cymonic"],
    ),
    make_record(
        "On 19 September 2026, from 2:00 PM to 3:00 PM at the CETAA Hall, the AI Summit hosts a panel discussion titled 'AI Defined Vehicles: Transforming the Industry.' Four confirmed speakers take part, all from the Automotive Vertical at Quest Global. Jeena Paulson is a Program Manager, Divya M S is a Technical Architect, Rakesh V M is a Technical Architect, and Fathima Jinna is a Project Manager. The point of contact for this session is Aiveen.",
        event_name="AI Defined Vehicles: Transforming the Industry",
        day=2,
        date="2026-09-19",
        category="panel",
        organizers=["Quest Global"],
    ),
    make_record(
        "Day 3 of the AI Summit at Drishti 2026 has four sessions. At 10:00 AM the EEE Seminar Hall hosts a talk on AI in healthcare. At 10:30 AM the CGPU Hall hosts a panel on large language models in the car cockpit. At 1:30 PM the CGPU Hall hosts a panel on the intelligent cockpit. At 2:30 PM the CETAA Hall hosts a panel on AI and the future of jobs.",
        event_name="AI Summit Day 3 Overview",
        day=3,
        date="2026-09-20",
        category="summit",
    ),
    make_record(
        "On 20 September 2026, from 10:00 AM to 11:00 AM at the EEE Seminar Hall, the AI Summit hosts a solo talk session titled 'AI in Healthcare: Diagnosing Fast.' The speaker is Anup G Prasad, Lead AI Engineer at Equipo Health, and his participation is confirmed. The point of contact for this session is Aiveen.",
        event_name="AI in Healthcare: Diagnosing Fast",
        day=3,
        date="2026-09-20",
        category="talk",
        organizers=["Equipo Health"],
    ),
    make_record(
        "On 20 September 2026, from 10:30 AM to 11:30 AM at the CGPU Hall, the AI Summit hosts a panel discussion titled 'The Car That Talks Back: LLMs in the Cockpit, from Voice Assistant to Co-Driver.' Four confirmed speakers take part, all from the Automotive Vertical at Quest Global. Anu A is a Principal Architect, Siva Prasad V is a Senior Technical Architect, Gigish Vadakkeparambathu is a Project Manager, and Lalkishor G is part of the automotive vertical team. The point of contact for this session is Aiveen.",
        event_name="The Car That Talks Back: LLMs in the Cockpit",
        day=3,
        date="2026-09-20",
        category="panel",
        organizers=["Quest Global"],
    ),
    make_record(
        "On 20 September 2026, from 1:30 PM to 2:30 PM at the CGPU Hall, the AI Summit hosts a panel discussion titled 'Intelligent Cockpit: The Car That Learns.' Four confirmed speakers take part, all from the Automotive Vertical at Quest Global. Vineesh C is a Senior Technical Architect, Shiney A John is a Program Manager, Lim Gopinath is a Delivery Manager, and Nishad Azeez is a Program Manager. The point of contact for this session is Aiveen.",
        event_name="Intelligent Cockpit: The Car That Learns",
        day=3,
        date="2026-09-20",
        category="panel",
        organizers=["Quest Global"],
    ),
    make_record(
        "On 20 September 2026, from 2:30 PM to 3:30 PM at the CETAA Hall, the AI Summit hosts a panel discussion titled 'Will AI Take Our Jobs?' Three confirmed speakers take part. Akhil A Vijay is Global Leader for Referral Hiring and Talent Marketing at Quest Global. Rejah Rehim is the Co-Founder and CEO of Beagle Security. Varghese Cherian is Head of Technology at UST. The point of contact for this session is Aiveen.",
        event_name="Will AI Take Our Jobs?",
        day=3,
        date="2026-09-20",
        category="panel",
        organizers=["Quest Global", "Beagle Security", "UST"],
    ),
    make_record(
        "Quest Global contributes the largest speaker contingent to the AI Summit at Drishti 2026, with twelve speakers across four sessions: Jeevadas K Y on the women in tech panel; Jeena Paulson, Divya M S, Rakesh V M and Fathima Jinna on the AI-defined vehicles panel; Anu A, Lalkishor G, Siva Prasad V and Gigish Vadakkeparambathu on the LLMs in the cockpit panel; Vineesh C, Shiney A John, Lim Gopinath and Nishad Azeez on the intelligent cockpit panel; and Akhil A Vijay on the future of jobs panel. Equipo Health contributes two speakers, Dr Aswathy Udayan and Anup G Prasad. Cymonic contributes two speakers, Sreejith Vadakara and Akhil Pulikkal Nandakumar. Government and public-sector speakers include Anoop Ambika of Kerala Startup Mission, Dr Sabarish Karunakaran of the Kerala State IT Mission, Ankit Asokan IPS of the Kerala Police Cyberdome, and Anoop Gopinath of SCTIMST. Startup and industry founders include Dr Shivoh Chirayil Nandakumar of RideScan, Mariyam Vidhu Vijayan of Crink, and Rejah Rehim of Beagle Security. Other speakers include Tony Thomas, Board Director at EQT, Varghese Cherian, Head of Technology at UST, and Advocate Jince T Thomas, an independent cyber lawyer.",
        event_name="Speaker Index by Organisation",
        day=None,
        date=None,
        category="speaker-index",
        organizers=["Quest Global", "Equipo Health", "Cymonic", "Kerala Startup Mission", "RideScan", "Crink", "Beagle Security", "EQT", "UST"],
    ),
    make_record(
        "The CETAA Hall hosts four sessions: AI in the automotive industry on 18 September at 1:30 PM, AI for Everyone on 19 September at 12:00 PM, AI-defined vehicles on 19 September at 2:00 PM, and Will AI Take Our Jobs on 20 September at 2:30 PM. The CGPU Hall hosts four sessions: Women in Tech on 18 September at 12:00 PM, AI for Governance on 19 September at 11:00 AM, the LLMs in the cockpit panel on 20 September at 10:30 AM, and the intelligent cockpit panel on 20 September at 1:30 PM. The EEE Seminar Hall hosts two sessions: the cyber fraud talk on 18 September at 2:30 PM and the AI in healthcare talk on 20 September at 10:00 AM, along with the medical devices talk on 19 September at 10:30 AM. The J C Alexander Hall hosts one session, the Kerala Startup Mission talk on 19 September at 10:00 AM.",
        event_name="Venue Index",
        category="venue-index",
    ),
    make_record(
        "Aiveen is the point of contact for the majority of AI Summit sessions, covering the women in tech panel, the Tony Thomas slot on the automotive panel, the medical devices talk, the AI for Everyone panel, the AI-defined vehicles panel, the AI in healthcare talk, the LLMs in the cockpit panel, the intelligent cockpit panel, and the Will AI Take Our Jobs panel. Devika Sajeesh is the point of contact for Dr Shivoh Chirayil Nandakumar. Akshay V Sarma is the point of contact for the cyber fraud talk by Advocate Jince T Thomas. Gautam is the point of contact for Anoop Ambika. Avaneesh is the point of contact for Dr Sabarish Karunakaran, and Abhimanyu is the point of contact for Ankit Asokan IPS.",
        event_name="Point of Contact Index",
        category="contact-index",
    ),
]

POSTER_DESCRIPTIONS = [
    {
        "id": "poster-ai-summit-overview",
        "image_name": "drishti-2026-ai-summit-overview-poster.png",
        "description": "Drishti 2026 AI Summit overview poster showing a three-day AI speaker programme with themes in automotive, governance, healthcare, and access to AI.",
        "search_text": "Drishti 2026 AI Summit overview poster three-day programme automotive governance healthcare access equity women in technology",
        "festival": "Drishti",
        "edition": 2026,
        "kind": "image",
    },
    {
        "id": "poster-ai-summit-day-1",
        "image_name": "drishti-2026-ai-summit-day-1-poster.png",
        "description": "Drishti 2026 AI Summit Day 1 poster featuring women in technology, AI in automotive, and cybersecurity governance sessions.",
        "search_text": "Drishti 2026 AI Summit Day 1 poster women in technology automotive industry cyber fraud governance LLMs",
        "festival": "Drishti",
        "edition": 2026,
        "kind": "image",
    },
    {
        "id": "poster-ai-summit-day-2",
        "image_name": "drishti-2026-ai-summit-day-2-poster.png",
        "description": "Drishti 2026 AI Summit Day 2 poster highlighting AI for governance, access and equity in AI, AI-defined vehicles, and medical devices sessions.",
        "search_text": "Drishti 2026 AI Summit Day 2 poster AI for governance access and equity in AI medical devices AI-defined vehicles",
        "festival": "Drishti",
        "edition": 2026,
        "kind": "image",
    },
    {
        "id": "poster-ai-summit-day-3",
        "image_name": "drishti-2026-ai-summit-day-3-poster.png",
        "description": "Drishti 2026 AI Summit Day 3 poster covering AI in healthcare, intelligent cockpit, LLMs in the cockpit, and the future of work panel.",
        "search_text": "Drishti 2026 AI Summit Day 3 poster AI in healthcare intelligent cockpit LLMs in the cockpit future of jobs",
        "festival": "Drishti",
        "edition": 2026,
        "kind": "image",
    },
]


def build_real_poster_records():
    entries = []
    if not POSTER_DOCS.exists():
        return entries

    allowed = {".png", ".jpg", ".jpeg", ".webp"}
    for image_path in sorted(POSTER_DOCS.iterdir()):
        if image_path.is_file() and image_path.suffix.lower() in allowed:
            stem = image_path.stem.replace("_", " ").replace("-", " ")
            name_lower = image_path.name.lower()
            poster_days = [1, 2, 3]
            if "day-1" in name_lower or "day1" in name_lower:
                poster_days = [1]
            elif "day-2" in name_lower or "day2" in name_lower:
                poster_days = [2]
            elif "day-3" in name_lower or "day3" in name_lower:
                poster_days = [3]
            relative_path = f"posters/{image_path.name}"
            entry = {
                "id": f"poster-{image_path.stem}",
                "source_text": f"Poster image for Drishti 2026: {stem}. This poster belongs to the Drishti 2026 AI Summit or event programme series.",
                "search_text": f"Drishti 2026 poster {stem} AI Summit event festival image {stem}",
                "festival": "Drishti",
                "edition": 2026,
                "days": poster_days,
                "dates": [
                    "2026-09-18" if 1 in poster_days else "",
                    "2026-09-19" if 2 in poster_days else "",
                    "2026-09-20" if 3 in poster_days else "",
                ],
                "categories": ["poster"],
                "organizers": [],
                "event_name": image_path.name,
                "is_scheduled": True,
                "is_listable": True,
                "kind": "image",
                "image_name": image_path.name,
                "image_path": relative_path,
            }
            entry["dates"] = [d for d in entry["dates"] if d]
            entries.append(entry)
    return entries


def assign_event_posters(records):
    for record in records:
        if record.get("poster_path"):
            continue
        event_name = (record.get("event_name") or "").strip()
        source_text = (record.get("source_text") or "").lower()
        haystack = f"{event_name.lower()} {source_text}"
        matched_path = None
        for key, value in WORKSHOP_POSTER_MAP.items():
            if key in haystack:
                matched_path = value
                break
        if matched_path:
            record["poster_path"] = matched_path
    return records


def main():
    existing = []
    if DATA_PATH.exists():
        existing = json.loads(DATA_PATH.read_text(encoding="utf-8"))

    records = assign_event_posters(existing + AI_SUMMIT_RECORDS)
    poster_records = build_real_poster_records()
    if poster_records:
        records.extend(poster_records)
    else:
        for entry in POSTER_DESCRIPTIONS:
            records.append(
                {
                    "id": entry["id"],
                    "source_text": entry["description"],
                    "search_text": entry["search_text"],
                    "festival": entry["festival"],
                    "edition": entry["edition"],
                    "days": [],
                    "dates": ["2026-09-18", "2026-09-19", "2026-09-20"],
                    "categories": ["poster"],
                    "organizers": [],
                    "event_name": entry["image_name"],
                    "is_scheduled": True,
                    "is_listable": True,
                    "kind": entry["kind"],
                    "image_name": entry["image_name"],
                }
            )

    merged = {}
    for record in records:
        key = record.get("event_name") or record.get("id") or record.get("source_text") or record.get("image_name")
        if key not in merged:
            merged[key] = record.copy()
            continue
        existing = merged[key]
        for field_name, field_value in record.items():
            if field_value not in (None, "", [], {}, ()):
                existing[field_name] = field_value
        merged[key] = existing
    deduped = list(merged.values())
    DATA_PATH.write_text(json.dumps(deduped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    POSTER_DOCS.mkdir(parents=True, exist_ok=True)
    POSTER_INDEX.write_text(json.dumps(POSTER_DESCRIPTIONS if not poster_records else [
        {
            "id": item["id"],
            "image_name": item["image_name"],
            "image_path": item.get("image_path", f"posters/{item['image_name']}"),
            "description": item["source_text"],
            "search_text": item["search_text"],
        }
        for item in poster_records
    ], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Merged {len(AI_SUMMIT_RECORDS)} AI Summit text records and {len(poster_records or POSTER_DESCRIPTIONS)} poster metadata entries into {DATA_PATH.name}")
    print(f"Poster index written to {POSTER_INDEX}")


if __name__ == "__main__":
    main()
