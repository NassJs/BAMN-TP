# AssistKB Search

Bienvenue dans le projet **AssistKB Search** ! 
Ce projet est un moteur de recherche sémantique et documentaire (RAG - Retrieval-Augmented Generation) conçu pour analyser, indexer et rechercher efficacement des informations dans une base de connaissances (Knowledge Base).

## 🚀 Fonctionnalités Actuelles (Role R2 - Indexation)

L'application est capable d'ingérer des fragments de textes (chunks), de les vectoriser à l'aide de modèles de langage (LLM), et de les stocker dans une base de données vectorielle ultra-rapide pour des recherches sémantiques.

* **Vectorisation Sémantique :** Utilisation de `sentence-transformers` avec le modèle performant `all-MiniLM-L6-v2` pour générer des embeddings de 384 dimensions.
* **Stockage Vectoriel :** Intégration complète avec **Qdrant** (via Docker) pour un stockage et une recherche optimisés.
* **Recherche Interactive :** Script de test interactif permettant de poser des questions en langage naturel et de récupérer les documents les plus pertinents.

## 📁 Architecture du Projet

```text
BAMN-TP/
├── app/
│   └── embedding/
│       ├── embed.py      # Script principal d'ingestion et de vectorisation des données
│       ├── search.py     # Script interactif pour tester la recherche sémantique
│       └── store.py      # Classe QdrantStore pour la gestion de la BDD vectorielle
├── corpus/               # Dossier contenant les données brutes et préparées
│   └── chunks.jsonl      # Base de connaissances (ex: CERT-FR, guides, etc.)
├── qdrant_data/          # Volume local pour la persistance de la BDD Qdrant
├── .env                  # Fichier des variables d'environnement (API keys, ports)
└── README.md             # Ce fichier
```

## 🛠️ Prérequis et Installation

1. **Python 3.10+**
2. **Docker** (pour exécuter Qdrant)

### 1. Démarrer Qdrant
Lancez la base de données vectorielle en tâche de fond avec Docker :
```bash
docker run -p 6333:6333 -v $(pwd)/qdrant_data:/qdrant/storage qdrant/qdrant
```

### 2. Environnement virtuel
Il est fortement recommandé d'utiliser un environnement virtuel local (`.venv`) pour installer les dépendances :
```bash
pip install -r requirements.txt
# (Inclut notamment qdrant-client, sentence-transformers, torch)
```

## 💻 Utilisation

### Indexation des données
Pour lire le fichier `corpus/chunks.jsonl`, générer les embeddings et les envoyer dans Qdrant :
```bash
python -m app.embedding.embed
```

### Tester la recherche
Une fois les données indexées, vous pouvez interroger la base en langage naturel :
```bash
python -m app.embedding.search
```

---
*Projet développé dans le cadre du TP RAG/LLM (Branche R2).*