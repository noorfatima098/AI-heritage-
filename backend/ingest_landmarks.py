# -*- coding: utf-8 -*-
"""
ingest_landmarks.py

Loads all landmark PDFs from a folder, splits each one into
section-based chunks (Basic Facts / Construction Details / Historical
Background / Trivia / Scenario), embeds them, and stores them in a
local ChromaDB collection for the AI Heritage Revive RAG pipeline.

Usage:
    python ingest_landmarks.py

Folder layout expected:
    research_pdfs/
        sheesh-mahal.pdf
        naulakha-pavilion.pdf
        ...

Output:
    A local persistent ChromaDB store at ./chroma_db, with one
    collection called "lahore_fort_landmarks".
"""

import os
import re
import pdfplumber
import chromadb

# ---------------------------------------------------------------------
# CONFIG — change these two paths if your folder names differ
# ---------------------------------------------------------------------
PDF_FOLDER = "research_pdfs"       # folder containing the 26 landmark PDFs
CHROMA_PATH = "vectordb"           # reuses your existing vectordb/ folder
COLLECTION_NAME = "lahore_fort_landmarks"

# Section headings as they appear in the generated PDFs.
# The script uses these to split each PDF into clean, topic-focused chunks
# instead of a raw word-count split — this keeps each chunk about ONE
# section (e.g. only "Construction Details"), which gives cleaner
# retrieval than mixed-topic chunks.
SECTION_HEADERS = [
    "1. Basic Facts",
    "2. Construction Details",
    "3. Historical Background",
    "4. Interesting Facts / Trivia",
    "5. Scenario / Narrative Moment",
]


def extract_text(pdf_path: str) -> str:
    """Extract raw text from a PDF, page by page."""
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    full_text = "\n".join(text_parts)
    # Strip the stray "l" artifact pdfplumber leaves behind from the
    # bullet-point glyphs used in the PDF (a rendering/extraction quirk,
    # not part of the actual content).
    full_text = re.sub(r"(?m)^l\s+", "", full_text)
    # Strip the standard footer line every landmark PDF ends with, so it
    # doesn't get swept into the last section's chunk (and from there,
    # into the Groq prompt). Uses an explicit word-for-word sequence
    # (whitespace-flexible only) rather than a DOTALL wildcard — a wildcard
    # span is unsafe here because "AI Heritage Revive" also appears inside
    # some landmarks' legitimate trivia content (e.g. postern-gate
    # references the project by name), and a greedy/lazy ".*?" would
    # incorrectly eat everything between that inner mention and the real
    # footer at the very end of the document.
    full_text = re.sub(
        r"AI Heritage Revive\s*[—-]\s*Lahore Fort landmark reference\.\s*"
        r"Compiled from encyclopedic research report;\s*figures marked\s*"
        r'"Not documented"\s*are\s*intentionally left blank rather than estimated\.',
        "",
        full_text,
    )
    return full_text


def split_into_sections(full_text: str) -> dict:
    """
    Split a landmark's full extracted text into a dict of
    {section_name: section_text}, using SECTION_HEADERS as split points.
    Anything before the first recognised heading (i.e. the title) is
    kept separately as "title".
    """
    # Build a regex that finds any of the section headers as a line
    pattern = "|".join(re.escape(h) for h in SECTION_HEADERS)
    matches = list(re.finditer(pattern, full_text))

    sections = {}
    if not matches:
        # Fallback: no recognisable headings found, treat whole text as one chunk
        sections["full_text"] = full_text.strip()
        return sections

    # Everything before the first heading = title/header block
    title_block = full_text[: matches[0].start()].strip()
    if title_block:
        sections["title"] = title_block

    for i, m in enumerate(matches):
        section_name = m.group()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        section_text = full_text[start:end].strip()
        if section_text:
            sections[section_name] = section_text

    return sections


def chunk_landmark_pdf(pdf_path: str, landmark_id: str) -> list:
    """
    Returns a list of chunk dicts for one landmark PDF:
    [{"id": ..., "text": ..., "metadata": {...}}, ...]
    One chunk per section — this matches the PDF's own template structure,
    so retrieval naturally comes back topic-focused (e.g. a "how was it built"
    question retrieves the Construction Details chunk specifically).
    """
    full_text = extract_text(pdf_path)
    sections = split_into_sections(full_text)

    chunks = []
    for section_name, section_text in sections.items():
        if section_name == "title":
            continue  # title text alone isn't useful as a standalone retrievable chunk
        chunk_id = f"{landmark_id}::{section_name}"
        chunks.append({
            "id": chunk_id,
            "text": f"{section_name}\n{section_text}",  # keep the heading in the chunk for context
            "metadata": {
                "landmark_id": landmark_id,
                "section": section_name,
                "source_file": os.path.basename(pdf_path),
            },
        })
    return chunks


def main():
    if not os.path.isdir(PDF_FOLDER):
        raise SystemExit(
            f"Folder '{PDF_FOLDER}' not found. Put your 26 landmark PDFs there, "
            f"or edit PDF_FOLDER at the top of this script."
        )

    # Persistent local ChromaDB client — data survives between runs
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # get_or_create so re-running the script doesn't error out;
    # ChromaDB's default embedding function (all-MiniLM-L6-v2, runs locally,
    # no API key or cost) is used automatically since we don't pass one.
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    all_ids, all_docs, all_metas = [], [], []

    pdf_files = sorted(f for f in os.listdir(PDF_FOLDER) if f.lower().endswith(".pdf"))
    if not pdf_files:
        raise SystemExit(f"No PDFs found in '{PDF_FOLDER}'.")

    print(f"Found {len(pdf_files)} PDFs. Extracting and chunking...\n")

    for filename in pdf_files:
        landmark_id = filename[:-4]  # strip ".pdf"
        pdf_path = os.path.join(PDF_FOLDER, filename)
        chunks = chunk_landmark_pdf(pdf_path, landmark_id)

        for chunk in chunks:
            all_ids.append(chunk["id"])
            all_docs.append(chunk["text"])
            all_metas.append(chunk["metadata"])

        print(f"  {landmark_id}: {len(chunks)} chunks")

    print(f"\nTotal chunks to add: {len(all_ids)}")

    # Upsert = safe to re-run; existing IDs get updated instead of duplicated
    collection.upsert(
        ids=all_ids,
        documents=all_docs,
        metadatas=all_metas,
    )

    print(f"\nDone. Collection '{COLLECTION_NAME}' now has {collection.count()} chunks "
          f"stored at ./{CHROMA_PATH}")


if __name__ == "__main__":
    main()