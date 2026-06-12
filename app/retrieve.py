from sentence_transformers import SentenceTransformer
from app.embedding.store import QdrantStore

MODEL_NAME = "all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.7

model = SentenceTransformer(MODEL_NAME)
store = QdrantStore()

def retrieve(question: str, top_k: int = 5):

    query_vector = model.encode(question).tolist()

    results = store.search(query_vector, top_k=top_k)

    filtered = [
        hit for hit in results
        if hit.score >= SIMILARITY_THRESHOLD
    ]

    return filtered if filtered else []