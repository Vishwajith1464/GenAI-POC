import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from legacy.rag_poc.embedding_model import model as embedding_model

model = embedding_model

def retrieve_chunks(
    question: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:

    if not question.strip() or not chunks:
        return []
    # 1. Convert the question into an embedding
    question_vector = model.encode(question)

    # 2. Collect the stored chunk embeddings
    chunk_vectors = np.array([
        chunk["embedding"] for chunk in chunks
    ])

    # 3. Calculate cosine similarity
    scores = cosine_similarity(
        question_vector.reshape(1, -1),
        chunk_vectors,
    )[0]

    # 4. Get indices of the highest-scoring chunks
    ranked_indices = np.argsort(scores)[::-1][:top_k]

    # 5. Return the matching chunks with their scores
    return [
        {
            **chunks[i],
            "similarity": float(scores[i]),
        }
        for i in ranked_indices
    ]
