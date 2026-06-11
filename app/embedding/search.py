import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
from app.store import QdrantStore

MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print(f"Chargement du modèle {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Connexion à Qdrant...")
    store = QdrantStore()
    
    # On vérifie que la collection existe bien
    store.ensure_collection()

    while True:
        query = input("\nEntrez votre question (ou 'exit' pour quitter) : ")
        if query.lower() in ['exit', 'quit']:
            break
            
        print("Recherche en cours...")
        
        # 1. On transforme la question en vecteur
        query_vector = model.encode(query).tolist()
        
        # 2. On cherche les 2 résultats les plus proches dans la base
        results = store.search(query_vector, top_k=2)
        
        if not results:
            print("Aucun résultat trouvé.")
            continue
            
        print("\n--- Résultats ---")
        for i, hit in enumerate(results):
            score = round(hit.score, 4)
            # hit.payload contient les données qu'on avait insérées (text, metadata)
            text = hit.payload.get("text", "Pas de texte")
            source = hit.payload.get("source", "Inconnue")
            print(f"{i+1}. Score: {score} | Source: {source}")
            print(f"   Texte: {text}")

if __name__ == "__main__":
    main()
