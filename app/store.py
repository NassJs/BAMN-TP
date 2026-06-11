import os
from qdrant_client import QdrantClient
from qdrant_client.http import models

class QdrantStore:
    def __init__(self):
        # On se connecte à l'instance Qdrant locale sur le port par défaut
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = "assistkb_collection"
        # ATTENTION : La dimension doit absolument être 384 pour le modèle all-MiniLM-L6-v2
        self.embedding_dim = 384 

    def ensure_collection(self):
        """Vérifie si la collection existe, sinon la crée (Idempotence)"""
        if not self.client.collection_exists(self.collection_name):
            print(f"[Store] Création de la collection '{self.collection_name}'...")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.embedding_dim,
                    distance=models.Distance.COSINE # Distance requise pour la similarité
                )
            )
        else:
            print(f"[Store] La collection '{self.collection_name}' existe déjà.")

    def upsert(self, points):
        """Insère les vecteurs et leurs métadonnées par lot"""
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
    def search(self, query_vector, top_k=5):
        """Cherche les vecteurs les plus proches"""
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k
        )