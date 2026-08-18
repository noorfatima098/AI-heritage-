# -*- coding: utf-8 -*-
"""
generate_narrative.py

Given a landmark_id (the same id your classifier outputs, e.g. "sheesh-mahal"
or "hathi-paer-stairs"), this module:
  1. Resolves classifier-specific naming differences to the actual PDF/
     ChromaDB slug (see LANDMARK_ALIASES below).
  2. Retrieves that landmark's stored chunks from ChromaDB by metadata
     filter — NOT semantic search — since we already know exactly which
     landmark we want, this guarantees complete, correct retrieval instead
     of relying on embedding similarity.
  3. Builds a grounded prompt from those chunks (with a different framing
     for the two Picture Wall "topic" entries — see TOPIC_ENTRIES).
  4. Calls Groq (llama-3.3-70b-versatile) to generate the visitor-facing
     narrative, instructed to never invent facts beyond the source material.

Usage from main.py (reusing your already-created chroma_client / groq_client
so this doesn't open a second ChromaDB connection):

    from generate_narrative import generate_narrative
    text = generate_narrative(landmark_id, chroma_client=chroma_client, groq_client=groq_client)

Standalone test (creates its own clients):

    python generate_narrative.py sheesh-mahal
"""

import os
import sys
import chromadb
from dotenv import load_dotenv
from groq import Groq

load_dotenv()  # reads GROQ_API_KEY from your .env file

VECTORDB_PATH = "vectordb"
COLLECTION_NAME = "lahore_fort_landmarks"
GROQ_MODEL = "openai/gpt-oss-120b"

# Order sections should appear in the prompt, so the narrative flows logically
SECTION_ORDER = [
    "1. Basic Facts",
    "2. Construction Details",
    "3. Historical Background",
    "4. Interesting Facts / Trivia",
    "5. Scenario / Narrative Moment",
]

# Your classifier's labels.txt uses slightly different slugs than the PDF
# filenames in research_pdfs/ for these landmarks. This maps the
# classifier's landmark_id -> the actual PDF/collection landmark_id, so
# main.py can pass the raw classifier output straight in without needing
# to know about the naming difference.
# (akbari-gate, alamgiri-gate, arz-gah, barood-khana, doulat-khana,
#  haveli-mai-jindan, maktab-khana, moti-masjid, shah-jahan-quadrangle,
#  sheesh-mahal all match exactly already, so they need no alias.)
LANDMARK_ALIASES = {
    "hathi-paer-stairs": "elephant-path",
    "jahangir-quadrangle": "jahangir-s-quadrangle-and-khwabgah-i-jahangiri",
    "lal-burj": "kala-burj-and-lal-burj",
    "picture-wall": "the-picture-wall",
    "royal-kitchen": "royal-kitchens",
    "diwan-i-amm": "diwan-i-aam",
}

# These two entries are conservation/history TOPICS about the Picture Wall,
# not physical structures a visitor stands in front of separately — they
# get a different narrative framing (storytelling, not "you are standing
# here right now"). Not reachable from your classifier (they aren't
# labels.txt classes), but included for when you surface them elsewhere
# in the app (e.g. an "explore" card).
TOPIC_ENTRIES = {"damage-and-causes", "restoration-project"}

_chroma_client = None
_collection = None
_groq_client = None


def resolve_landmark_id(landmark_id: str) -> str:
    """Map a classifier-output landmark_id to the slug actually used in
    research_pdfs/ and the vectordb, via LANDMARK_ALIASES. Passes through
    unchanged if there's no alias (i.e. the names already match)."""
    return LANDMARK_ALIASES.get(landmark_id, landmark_id)


def _get_collection(chroma_client=None):
    """
    If `chroma_client` is passed in (e.g. from main.py), reuse it — this
    avoids opening a second ChromaDB connection to the same vectordb/
    folder in one process, which can cause "database is locked" errors.
    Otherwise, lazily create a standalone client (only happens when this
    module is run directly: `python generate_narrative.py sheesh-mahal`).
    """
    global _chroma_client, _collection
    if chroma_client is not None:
        return chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    if _collection is None:
        _chroma_client = chromadb.PersistentClient(path=VECTORDB_PATH)
        _collection = _chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return _collection


def _get_groq_client(groq_client=None):
    global _groq_client
    if groq_client is not None:
        return groq_client
    if _groq_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Add it to your .env file in backend/ as:\n"
                "GROQ_API_KEY=your_key_here"
            )
        _groq_client = Groq(api_key=api_key)
    return _groq_client


def retrieve_landmark_chunks(landmark_id: str, chroma_client=None):
    """
    Fetch all stored chunks for one landmark, keyed by section name.
    Resolves classifier-output ids through LANDMARK_ALIASES first, then
    uses a metadata filter (collection.get with where=) — not a semantic
    query — since we already know the exact landmark, this pulls back the
    complete, correct set of sections every time.

    Returns (sections_dict, resolved_id).
    Raises ValueError if nothing is found (e.g. not yet ingested, or a
    genuinely unmapped landmark_id).
    """
    resolved_id = resolve_landmark_id(landmark_id)
    collection = _get_collection(chroma_client)
    result = collection.get(where={"landmark_id": resolved_id})

    if not result["ids"]:
        raise ValueError(
            f"No chunks found for landmark_id='{landmark_id}' (resolved to '{resolved_id}'). "
            f"Check it matches a filename in research_pdfs/ (without .pdf), or add an alias "
            f"to LANDMARK_ALIASES, and that you've run ingest_landmarks.py."
        )

    sections = {}
    for doc, meta in zip(result["documents"], result["metadatas"]):
        sections[meta["section"]] = doc
    return sections, resolved_id


def build_prompt(resolved_id: str, sections: dict, tone: str = "warm, knowledgeable tour guide") -> str:
    """Combine the retrieved section chunks into a single grounded prompt for Groq."""
    display_name = resolved_id.replace("-", " ").title().replace(" And ", " and ")

    ordered_context = []
    for section_name in SECTION_ORDER:
        if section_name in sections:
            ordered_context.append(sections[section_name])
    context = "\n\n".join(ordered_context)

    if resolved_id in TOPIC_ENTRIES:
        # Storytelling framing — no "you are standing in front of it" language,
        # since this isn't a physical spot on the visitor's map.
        prompt = f"""You are a {tone} explaining a specific chapter in the story of Lahore Fort's Picture Wall to a visitor using an AI heritage app: "{display_name}".

Use ONLY the facts given below. Do not invent dates, costs, names, or numbers that are not present in this material. If something is marked "Not documented," do not guess a value to fill the gap — simply leave it out of the narrative.

--- SOURCE MATERIAL ---
{context}
--- END SOURCE MATERIAL ---

Write a vivid, engaging 150-200 word explanation of this topic. Do NOT frame it as the visitor standing in front of a specific spot — instead, tell it as a short, compelling piece of the wall's history (what happened, why it mattered). Blend in the scenario/narrative moment provided above naturally. End with one genuinely interesting detail."""
        return prompt

    prompt = f"""You are a {tone} narrating the history of "{display_name}", a monument inside Lahore Fort, for a visitor using an AI heritage app who is standing in front of it right now.

Use ONLY the facts given below. Do not invent dates, costs, names, or numbers that are not present in this material. If something is marked "Not documented," do not guess a value to fill the gap — simply leave it out of the narrative.

--- SOURCE MATERIAL ---
{context}
--- END SOURCE MATERIAL ---

Write a vivid, engaging 150-200 word narrative. Blend the historical facts naturally with the scenario/narrative moment provided above. End with one genuinely interesting detail that would make the visitor want to look closer."""
    return prompt


def generate_narrative(landmark_id: str, tone: str = "warm, knowledgeable tour guide",
                        chroma_client=None, groq_client=None) -> str:
    """
    Full pipeline: resolve aliases, retrieve this landmark's chunks from
    ChromaDB, then ask Groq to turn them into a narrative grounded in
    those chunks.

    Pass chroma_client / groq_client (your already-created clients from
    main.py) to reuse them instead of opening new connections.
    """
    sections, resolved_id = retrieve_landmark_chunks(landmark_id, chroma_client)
    prompt = build_prompt(resolved_id, sections, tone)

    client = _get_groq_client(groq_client)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": "You are a careful, accurate heritage narrator. Never invent facts that are not in the material you are given."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    landmark = sys.argv[1] if len(sys.argv) > 1 else "sheesh-mahal"
    print(f"Generating narrative for: {landmark}\n")
    print(generate_narrative(landmark))