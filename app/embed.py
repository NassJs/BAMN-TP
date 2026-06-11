import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct

# On importe l'adaptateur store.py que tu as dû créer juste avant
from app.store import QdrantStore

MODEL_NAME = "all-MiniLM-L6-v2"
DATA_PATH = "corpus/chunks.jsonl"
BATCH_SIZE = 2 

def main():
    print(f"Chargement du modèle {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Initialisation de QdrantStore...")
    store = QdrantStore()
    store.ensure_collection()

    texts_batch = []
    payloads_batch = []
    
    print(f"Lecture du fichier {DATA_PATH}...")
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                chunk = json.loads(line)
                texts_batch.append(chunk["text"])
                
                payload = chunk.get("metadata", {})
                payload["text"] = chunk["text"]
                payloads_batch.append(payload)
                
                if len(texts_batch) == BATCH_SIZE:
                    process_batch(model, store, texts_batch, payloads_batch)
                    texts_batch = []
                    payloads_batch = []
                    
        if len(texts_batch) > 0:
            process_batch(model, store, texts_batch, payloads_batch)
            
        print("Indexation terminee avec succes !")
        
    except FileNotFoundError:
        print(f"Erreur : Le fichier {DATA_PATH} est introuvable. Demande au R1 de le generer !")

def process_batch(model, store, texts, payloads):
    print(f"Vectorisation d'un batch de {len(texts)} chunks...")
    embeddings = model.encode(texts) 
    
    points = []
    for i, embedding in enumerate(embeddings):
        point_id = str(uuid.uuid4())
        points.append(
            PointStruct(
                id=point_id,
                vector=embedding.tolist(),
                payload=payloads[i]
            )
        )
        
    print("Insertion dans Qdrant...")
    store.upsert(points)

if __name__ == "__main__":
    main()