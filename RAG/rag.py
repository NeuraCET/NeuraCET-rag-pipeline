"""RAG pipeline for Drishti / Daksha fest data.

Retrieval always runs against the full record text (dense embeddings +
BM25 keyword search, fused and optionally reranked). The context handed
to the LLM is a separate, token-budgeted compaction of the top results —
nothing is dropped from the searchable corpus, only from the prompt.
"""

import calendar
import hashlib
import json
import re
import sys
from pathlib import Path

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
CLEAN_DATA_PATH = ROOT / "clean_data.json"
POSTER_DIR = PROJECT_ROOT / "posters"
LEGACY_POSTER_DIR = PROJECT_ROOT / "data" / "posters"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
CACHE_DIR = ROOT / ".rag_cache"
CACHE_DIR.mkdir(exist_ok=True)

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
RERANK_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
USE_RERANKER = True
RRF_K = 60  # standard reciprocal-rank-fusion constant
IMAGE_GALLERY_WORDS = {"image", "images", "photo", "photos", "flyer", "flyers"}
STOP_WORDS = {
    "day", "days", "hosts", "host", "drishti", "daksha", "collaboration", "workshop",
    "competition", "talk", "panel", "session", "sessions", "features", "feature",
    "event", "conducted", "featuring", "edition", "with", "and", "the", "from", "for",
}
MONTH_WORDS = {calendar.month_name[i].lower() for i in range(1, 13)} | {
    calendar.month_abbr[i].lower() for i in range(1, 13)
}
NOISE_WORDS = STOP_WORDS | MONTH_WORDS

MONTH_TO_NUM = {}
for _i in range(1, 13):
    MONTH_TO_NUM[calendar.month_name[_i].lower()] = _i
    MONTH_TO_NUM[calendar.month_abbr[_i].lower()] = _i


# ---------------------------------------------------------------------------
# Data loading (unchanged behaviour, same output shape as before)
# ---------------------------------------------------------------------------

def load_poster_records():
    entries = []
    poster_root = POSTER_DIR if POSTER_DIR.exists() else LEGACY_POSTER_DIR
    index_path = poster_root / "poster_index.json"
    if index_path.exists():
        try:
            entries.extend(json.loads(index_path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            entries = []

    files = sorted(poster_root.glob("*")) if poster_root.exists() else []
    for file_path in files:
        if not file_path.is_file() or file_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        stem = file_path.stem.replace("_", " ").replace("-", " ")
        entries.append(
            {
                "id": f"poster-{file_path.stem}",
                "image_name": file_path.name,
                "image_path": str(file_path.relative_to(PROJECT_ROOT)),
                "description": f"Poster image for Drishti 2026: {stem}.",
                "search_text": f"Drishti 2026 poster {stem} {file_path.stem}",
                "festival": "Drishti",
                "edition": 2026,
                "days": [1, 2, 3],
                "dates": ["2026-09-18", "2026-09-19", "2026-09-20"],
                "kind": "image",
            }
        )

    deduped, seen = [], set()
    for entry in entries:
        key = entry.get("id") or entry.get("image_name") or entry.get("description")
        if key in seen:
            continue
        seen.add(key)
        deduped.append(entry)
    return deduped


def convert_image_entries_to_records(image_entries):
    records = []
    for entry in image_entries:
        image_path = entry.get("image_path") or str(
            POSTER_DIR / (entry.get("image_name") or entry.get("id") or "poster.png")
        )
        records.append(
            {
                "id": entry.get("id") or entry.get("image_name") or f"poster-{len(records)}",
                "source_text": entry.get("description") or entry.get("search_text") or "Poster image",
                "search_text": entry.get("search_text") or entry.get("description") or entry.get("image_name") or "Poster image",
                "festival": entry.get("festival") or "Drishti",
                "edition": entry.get("edition") or 2026,
                "days": entry.get("days") or [1, 2, 3],
                "dates": entry.get("dates") or ["2026-09-18", "2026-09-19", "2026-09-20"],
                "categories": ["poster", "image"],
                "organizers": [],
                "event_name": entry.get("image_name") or entry.get("id") or "Poster image",
                "is_scheduled": True,
                "is_listable": True,
                "kind": "image",
                "image_name": entry.get("image_name") or entry.get("id") or "Poster image",
                "image_path": image_path,
                "poster_path": image_path,
            }
        )
    return records


def load_records():
    records = json.loads(CLEAN_DATA_PATH.read_text(encoding="utf-8"))
    image_records = convert_image_entries_to_records(load_poster_records())
    return records + image_records


def normalize_text(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def tokenize(value):
    return normalize_text(value).split()


# ---------------------------------------------------------------------------
# Index build + on-disk cache (embeddings only get recomputed when the
# underlying text actually changes)
# ---------------------------------------------------------------------------

def _content_hash(records):
    payload = json.dumps(
        [{"id": r["id"], "search_text": r["search_text"]} for r in records],
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class RagIndex:
    def __init__(self):
        self.records = load_records()
        self.id_to_pos = {r["id"]: i for i, r in enumerate(self.records)}
        self._hash = _content_hash(self.records)

        self.model = SentenceTransformer(EMBED_MODEL_NAME)
        self.embeddings = self._load_or_build_embeddings()

        self.faiss_index = faiss.IndexFlatIP(self.embeddings.shape[1])
        self.faiss_index.add(self.embeddings)
        faiss.write_index(self.faiss_index, str(ROOT / "drishti.index"))
        np.save(ROOT / "drishti_chunks.npy", np.array([r["source_text"] for r in self.records]))

        self.bm25 = BM25Okapi([tokenize(r["search_text"]) for r in self.records])

        # Posters are attachments to an event, not competitors for it in text
        # search — a one-line "Poster image for X" doc will out-rank a real
        # paragraph on short/generic queries if it's left in the same pool.
        self.text_records = [r for r in self.records if r.get("kind") != "image"]
        self.image_records = [r for r in self.records if r.get("kind") == "image"]

        self._known_editions = sorted({r["edition"] for r in self.records if r.get("edition")})
        self._known_days = sorted({d for r in self.records for d in r.get("days", [])})
        self._category_aliases = self._build_category_aliases()
        self._reranker = None  # loaded lazily, only if actually used

        # "Day 2" only means something within one edition — 2024's day 2 and
        # 2026's day 2 are unrelated calendar days that happen to share a
        # number. Default to the current edition whenever the query doesn't
        # name a year explicitly, so listing queries don't silently blend
        # editions together.
        self.default_edition = max(self._known_editions) if self._known_editions else None

    def _load_or_build_embeddings(self):
        cache_path = CACHE_DIR / f"{self._hash}.npy"
        if cache_path.exists():
            return np.load(cache_path)
        texts = [r["search_text"] for r in self.records]
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        np.save(cache_path, embeddings)
        return embeddings

    def _build_category_aliases(self):
        # "image" is deliberately excluded here — it's handled separately as
        # a request for the raw poster gallery (see IMAGE_GALLERY_WORDS),
        # not as a normal content category like "workshop" or "talk".
        aliases = {}
        for r in self.records:
            for c in r.get("categories", []):
                if c == "image":
                    continue
                aliases[c] = c
                aliases[c + "s" if not c.endswith("s") else c] = c
        return aliases

    @property
    def reranker(self):
        if self._reranker is None:
            self._reranker = CrossEncoder(RERANK_MODEL_NAME)
        return self._reranker

    # -- metadata filters, derived from the data instead of hardcoded --------

    def extract_filters(self, query):
        lowered = query.lower()

        edition_match = re.search(r"\b(20\d{2})\b", lowered)
        edition = int(edition_match.group(1)) if edition_match else None
        if edition is not None and edition not in self._known_editions:
            edition = None  # ignore years that don't appear in the data at all
        explicit_edition = edition is not None

        day_match = re.search(r"\bday\s*([1-9])\b", lowered)
        day = int(day_match.group(1)) if day_match and int(day_match.group(1)) in self._known_days else None

        month_pattern = "|".join(sorted((re.escape(m) for m in MONTH_TO_NUM), key=len, reverse=True))
        date_match = re.search(rf"\b({month_pattern})\.?\s+(\d{{1,2}})\b", lowered)
        date_suffix = None
        if date_match:
            month_num = MONTH_TO_NUM[date_match.group(1)]
            day_num = int(date_match.group(2))
            date_suffix = f"{month_num:02d}-{day_num:02d}"

        category = next(
            (canon for alias, canon in self._category_aliases.items() if re.search(rf"\b{re.escape(alias)}\b", lowered)),
            None,
        )

        wants_image_gallery = any(re.search(rf"\b{w}\b", lowered) for w in IMAGE_GALLERY_WORDS)

        is_listing = bool(
            day or date_suffix or category
            or re.search(r"\b(list|all|what|which|happening|available|schedule)\b", lowered)
        )

        wants_historical = re.search(r"\b(previous|past|history|editions|earlier|before|ever)\b", lowered)
        if is_listing and not explicit_edition and not wants_historical and self.default_edition:
            edition = self.default_edition

        return {
            "edition": edition,
            "day": day,
            "date_suffix": date_suffix,
            "category": category,
            "wants_image_gallery": wants_image_gallery,
            "is_listing": is_listing,
        }

    def filter_pool(self, filters, base=None):
        pool = [r for r in (base if base is not None else self.text_records) if r.get("is_listable")]
        if filters["edition"]:
            pool = [r for r in pool if r.get("edition") == filters["edition"]]
        if filters["day"]:
            pool = [r for r in pool if filters["day"] in r.get("days", [])]
        if filters["date_suffix"]:
            pool = [r for r in pool if any(d.endswith(filters["date_suffix"]) for d in r.get("dates", []))]
        if filters["category"]:
            pool = [r for r in pool if filters["category"] in r.get("categories", [])]
        return pool

    # -- linking events to their poster image ---------------------------------

    def _distinctive_keywords(self, text):
        """Tokens worth matching on filenames — drops generic fest/event
        words and year/month tokens (present in nearly every record, so
        they only dilute the match) that collide across many files."""
        tokens = {
            t for t in tokenize(text)
            if len(t) >= 4 and t not in NOISE_WORDS and not t.isdigit()
        }
        return tokens or set(tokenize(text))

    def best_poster_match(self, record, min_score=0.3):
        """Match an event against raw poster filenames by substring
        containment, not token equality — most of these filenames are
        squashed together with no separators ("engineworkshop.jpeg",
        "signalshowdown.jpeg"), so exact word-token matching mostly fails.
        """
        keywords = self._distinctive_keywords(f"{record.get('event_name', '')} {record.get('source_text', '')}")
        if not keywords:
            return None
        best, best_score = None, 0.0
        for img in self.image_records:
            stem = normalize_text(Path(img.get("image_name", "")).stem).replace(" ", "")
            if not stem:
                continue
            hits = sum(1 for kw in keywords if kw in stem)
            score = hits / len(keywords)
            if score > best_score:
                best, best_score = img, score
        return best.get("image_path") if best and best_score >= min_score else None

    def attach_posters(self, results, max_posters=3):
        posters = []
        for record, _score in results:
            path = record.get("poster_path") or self.best_poster_match(record)
            if path and path not in posters:
                posters.append(path)
        return posters[:max_posters]

    def audit_poster_links(self):
        """Data-quality check, not used at query time: flags records whose
        stored poster_path disagrees with the best independent filename
        match, and records with no poster reference at all. Run this once
        after editing clean_data.json, not on every query."""
        mismatches, missing = [], []
        for r in self.text_records:
            stored = r.get("poster_path")
            guess = self.best_poster_match(r)
            if stored and guess and stored != guess:
                mismatches.append((r["id"], r.get("event_name", "")[:60], stored, guess))
            elif not stored and not guess:
                missing.append((r["id"], r.get("event_name", "")[:60]))
        print(f"{len(mismatches)} possible mislabeled poster_path value(s):")
        for rid, name, stored, guess in mismatches:
            print(f"  [{rid}] {name!r}: stored={stored}  best_guess={guess}")
        print(f"\n{len(missing)} record(s) with no poster reference at all:")
        for rid, name in missing:
            print(f"  [{rid}] {name!r}")

    # -- hybrid dense + lexical search, fused with RRF ------------------------

    def search(self, query, k=8, pool=None, rerank=USE_RERANKER):
        # Default pool is text_records only, so a one-line poster caption
        # never competes with an actual event write-up for the same query.
        candidates = pool if pool is not None else self.text_records
        if not candidates:
            return []
        positions = [self.id_to_pos[r["id"]] for r in candidates]

        query_vec = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
        dense_scores = self.embeddings[positions] @ query_vec
        dense_order = [positions[i] for i in np.argsort(-dense_scores)]

        bm25_scores = self.bm25.get_scores(tokenize(query))
        bm25_order = sorted(positions, key=lambda p: bm25_scores[p], reverse=True)

        rrf = {}
        for rank, pos in enumerate(dense_order):
            rrf[pos] = rrf.get(pos, 0.0) + 1.0 / (RRF_K + rank + 1)
        for rank, pos in enumerate(bm25_order):
            rrf[pos] = rrf.get(pos, 0.0) + 1.0 / (RRF_K + rank + 1)

        fused = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)
        top_pool = fused[: max(k * 3, k)]  # widen before reranking, then trim
        results = [(self.records[pos], score) for pos, score in top_pool]

        if rerank and results:
            try:
                pairs = [(query, r["source_text"]) for r, _ in results]
                cross_scores = self.reranker.predict(pairs)
                results = sorted(zip([r for r, _ in results], cross_scores), key=lambda kv: kv[1], reverse=True)
            except Exception:
                pass  # fall back to the RRF ordering if the reranker can't load

        return results[:k]


# ---------------------------------------------------------------------------
# Compact, token-budgeted context for a small-context LLM
# ---------------------------------------------------------------------------

def compact_summary(record):
    if record.get("kind") == "image":
        label = record.get("image_name") or record.get("event_name") or record.get("id")
        poster_path = record.get("poster_path") or record.get("image_path")
        return f"{label}" + (f" | poster: {poster_path}" if poster_path else "")

    source = record.get("source_text") or record.get("event_name") or ""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", source) if s.strip()]
    summary = sentences[0] if sentences else source
    if len(summary) > 200:
        summary = summary[:197].rstrip() + "..."

    event_name = record.get("event_name") or ""
    if event_name and event_name.lower() not in summary.lower():
        summary = f"{event_name}: {summary}"

    tags = []
    if record.get("days"):
        tags.append("day " + "/".join(str(d) for d in record["days"]))
    if record.get("categories"):
        tags.append(record["categories"][0])
    if tags:
        summary = f"[{', '.join(tags)}] {summary}"

    poster_path = record.get("poster_path")
    return summary + (f" | poster: {poster_path}" if poster_path else "")


def build_llm_context(results, max_chars=1600, max_items=12):
    """Turn ranked (record, score) pairs into a short, cited context block.

    The full record set stays fully searchable at all times; this only
    controls how much text actually goes into the LLM prompt. If more
    matches exist than fit the budget, that's stated explicitly rather
    than silently dropped.
    """
    lines, total, shown = [], 0, 0
    for record, _score in results[:max_items]:
        line = f"[{record['id']}] {compact_summary(record)}"
        if lines and total + len(line) > max_chars:
            break
        lines.append(line)
        total += len(line)
        shown += 1
    remaining = len(results) - shown
    if remaining > 0:
        lines.append(f"...and {remaining} more matching record(s) not shown here.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Query entry point
# ---------------------------------------------------------------------------

def run_query(index: RagIndex, query, k=6, max_listing_results=30):
    filters = index.extract_filters(query)

    if filters["wants_image_gallery"] and not filters["category"]:
        # explicit "show me the posters/photos" browsing, not an event question
        results = index.search(query, k=k, pool=index.image_records)
        print(f"Retrieved {len(results)} poster(s):")
        for i, (record, score) in enumerate(results, start=1):
            print(f"{i}. ({score:.3f}) {compact_summary(record)}")
        return results, [r.get("image_path") for r, _ in results], ""

    pool = index.filter_pool(filters) if filters["is_listing"] else None
    # A listing query (day/date/category filter matched) is a deterministic
    # membership test, not an open-ended similarity search — it should
    # return everything that matches the filter, not just a top-k slice.
    effective_k = min(len(pool), max_listing_results) if pool is not None else k
    results = index.search(query, k=effective_k, pool=pool)
    if not results and pool:
        results = index.search(query, k=k, pool=None)  # filters too narrow, fall back

    posters = index.attach_posters(results, max_posters=min(effective_k, 12))
    context = build_llm_context(results, max_items=effective_k)

    print(f"Retrieved {len(results)} record(s):")
    for i, (record, score) in enumerate(results, start=1):
        print(f"{i}. ({score:.3f}) {compact_summary(record)}")

    print("\n--- context handed to the LLM ---")
    print(context)
    print("----------------------------------")
    print(f"posters to show: {posters or 'none'}\n")
    return results, posters, context


if __name__ == "__main__":
    index = RagIndex()
    if "--audit-posters" in sys.argv:
        index.audit_poster_links()
        raise SystemExit(0)
    while True:
        query = input("Enter your query (or type 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        if query:
            run_query(index, query)