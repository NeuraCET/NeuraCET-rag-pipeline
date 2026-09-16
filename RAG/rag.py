import json
import re
import subprocess
import sys
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent
CLEAN_DATA_PATH = ROOT / "clean_data.json"


def load_records():
    return json.loads(CLEAN_DATA_PATH.read_text(encoding="utf-8"))


records = load_records()
model = SentenceTransformer("all-MiniLM-L6-v2")
search_texts = [record["search_text"] for record in records]
embeddings = model.encode(search_texts, convert_to_numpy=True, normalize_embeddings=True)

index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, str(ROOT / "drishti.index"))
np.save(ROOT / "drishti_chunks.npy", np.array([record["source_text"] for record in records]))


def extract_filters(query):
    lowered = query.lower()
    edition_match = re.search(r"\b(?:drishti|daksha)['’ -]*(20\d{2})\b", lowered)
    day_match = re.search(r"\bday\s*([1-3])\b", lowered)
    date_match = re.search(
        r"\b(?:september|sep)\s+(13|15|16|17|18|19|20)(?:,?\s*2026)?\b", lowered
    )
    category_aliases = {
        "workshop": "workshop",
        "workshops": "workshop",
        "competition": "competition",
        "competitions": "competition",
        "hackathon": "hackathon",
        "hackathons": "hackathon",
        "talk": "talk",
        "talks": "talk",
        "concert": "concert",
        "concerts": "concert",
        "expo": "expo",
        "expos": "expo",
    }
    category = next((value for key, value in category_aliases.items() if re.search(rf"\b{key}\b", lowered)), None)
    is_listing = bool(
        day_match
        or date_match
        or re.search(r"\b(list|all|what|which|happening|available|main things)\b", lowered)
    )
    return {
        "edition": int(edition_match.group(1)) if edition_match else (2026 if day_match else None),
        "day": int(day_match.group(1)) if day_match else None,
        "date": f"2026-09-{int(date_match.group(1)):02d}" if date_match else None,
        "category": category,
        "is_listing": is_listing,
    }


def metadata_search(query):
    filters = extract_filters(query)
    matches = [record for record in records if record["is_listable"]]
    if filters["edition"]:
        matches = [record for record in matches if record["edition"] == filters["edition"]]
    if filters["day"]:
        matches = [record for record in matches if filters["day"] in record["days"]]
    if filters["date"]:
        matches = [record for record in matches if filters["date"] in record["dates"]]
    if filters["category"]:
        matches = [record for record in matches if filters["category"] in record["categories"]]
    return matches, filters


def semantic_search(query, k=8):
    query_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, ids = index.search(query_embedding, min(k, len(records)))
    return [(records[index_id], float(scores[0][position])) for position, index_id in enumerate(ids[0])]


def print_metadata_results(matches, filters):
    if not matches:
        print("No matching scheduled records were found.")
        return
    scope = []
    if filters["edition"]:
        scope.append(f"Drishti {filters['edition']}")
    if filters["day"]:
        scope.append(f"Day {filters['day']}")
    if filters["date"]:
        scope.append(filters["date"])
    print(f"Found {len(matches)} matching records" + (f" ({', '.join(scope)})" if scope else "") + ":")
    for position, record in enumerate(matches, start=1):
        print(f"{position}. {record['source_text']}")


def run_query(query):
    matches, filters = metadata_search(query)
    if filters["is_listing"] and (filters["day"] or filters["date"] or filters["category"]):
        print_metadata_results(matches, filters)
        return
    for record, score in semantic_search(query):
        print(f"{score:.3f}  {record['source_text']}")


if __name__ == "__main__":
    while True:
        query = input("Enter your query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        if query:
            run_query(query)