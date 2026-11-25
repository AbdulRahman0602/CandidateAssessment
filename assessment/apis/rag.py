from sentence_transformers import SentenceTransformer
import os
import json
import faiss
import numpy as np
import fitz
from docx import Document

from django.conf import settings


def extract_resume_text(file_path):

    extension = file_path.split('.')[-1].lower()

    text = ""

    if extension == "pdf":

        pdf = fitz.open(file_path)

        for page in pdf:
            text += page.get_text() + "\n"

        pdf.close()

    elif extension == "docx":

        doc = Document(file_path)

        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        for table in doc.tables:
            for row in table.rows:
                text += " | ".join(
                    cell.text for cell in row.cells
                ) + "\n"

    else:
        raise ValueError("Unsupported resume format")

    if not text.strip():
        raise ValueError("No readable text found in resume")

    return text


def split_text_into_chunks(
    text,
    chunk_size=500,
    overlap=100
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# Load the embedding model
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def generate_embeddings(chunks):

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings


def create_faiss_index(chunks, embeddings, resume_id):

    # Create a folder for this resume
    index_dir = os.path.join(
        settings.MEDIA_ROOT,
        "faiss_indexes",
        f"resume_{resume_id}"
    )

    os.makedirs(index_dir, exist_ok=True)

    # Convert embeddings to float32
    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    # Embedding dimensions
    dimension = embeddings.shape[1]

    # Create FAISS index
    index = faiss.IndexFlatIP(dimension)

    # Add embeddings
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(
        index,
        os.path.join(index_dir, "index.faiss")
    )

    # Save corresponding text chunks
    with open(
        os.path.join(index_dir, "chunks.json"),
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(chunks, file, ensure_ascii=False)

    return index_dir



def process_resume(file_upload):

    # Step 1: Get uploaded file path
    file_path = file_upload.file.path

    # Step 2: Extract text
    resume_text = extract_resume_text(file_path)

    # Step 3: Split text
    chunks = split_text_into_chunks(
        resume_text,
        chunk_size=500,
        overlap=100
    )

    # Step 4: Generate embeddings
    embeddings = generate_embeddings(chunks)

    # Step 5: Create FAISS index
    index_dir = create_faiss_index(
        chunks,
        embeddings,
        file_upload.id
    )

    return {
        "resume_id": file_upload.id,
        "total_chunks": len(chunks),
        "index_location": index_dir,
        "message": "Resume processed successfully"
    }



def retrieve_resume_context(
    resume_id,
    query,
    top_k=5
):

    index_dir = os.path.join(
        settings.MEDIA_ROOT,
        "faiss_indexes",
        f"resume_{resume_id}"
    )

    index_path = os.path.join(
        index_dir,
        "index.faiss"
    )

    chunks_path = os.path.join(
        index_dir,
        "chunks.json"
    )

    if not os.path.exists(index_path):
        raise FileNotFoundError("FAISS index not found")

    # Load FAISS index
    index = faiss.read_index(index_path)

    # Load original chunks
    with open(chunks_path, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    # Generate query embedding
    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # Search FAISS
    k = min(top_k, index.ntotal)

    scores, indices = index.search(
        query_embedding,
        k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx == -1:
            continue

        results.append({
            "text": chunks[idx],
            "score": float(score)
        })

    return results


