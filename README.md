# BAMN-TP : Pipeline d'Ingestion, Indexation et Recherche LLM

Ce projet met en place une architecture complète permettant l'extraction de données, leur vectorisation, leur stockage dans une base de données vectorielle, et enfin l'interrogation de ces données via un modèle de langage (LLM).

## 🏗️ Architecture du Projet

Le projet est structuré autour de trois modules principaux (correspondant aux différentes phases de la donnée) :

*   **R1 - Ingestion (`/corpus`, `/script`) :** 
    Gestion de l'extraction brute et préparation des dossiers d'entrée pour le corpus de données (Projet A).
*   **R2 - Indexation (`/app/embedding`) :** 
    Génération des embeddings à partir du corpus et indexation dans la base de données vectorielle **Qdrant**.
*   **R3 - Retrieval LLM :** 
    Moteur de recherche permettant de requêter la base Qdrant et d'utiliser un LLM pour formuler des réponses contextualisées (RAG - Retrieval-Augmented Generation).
*  **R4 - Devops Containerisation :**
    Mise en place des containers 

## 🛠️ Prérequis

Avant de lancer le projet, assurez-vous de disposer des éléments suivants :
*   **Docker** et **Docker Compose** (tous les services sont conteneurisés).
*   Une clé API **Mistral** (pour la génération de réponses).
*   *(Optionnel)* **Python 3.11+** si vous souhaitez exécuter les scripts en local hors Docker.

## 🚀 Installation et Lancement

### 1. Cloner le dépôt

```bash
git clone git@github.com:NassJs/BAMN-TP.git
cd BAMN-TP
```

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
MISTRAL_API_KEY=votre_cle_api_mistral
```

### 3. Lancer les services avec Docker Compose

Le projet est composé de 4 services conteneurisés :

| Service     | Rôle                                              | Port |
|-------------|---------------------------------------------------|------|
| `qdrant`    | Base de données vectorielle                       | 6333 |
| `ingestion` | R1 — Extraction et découpage du corpus en chunks  | —    |
| `embedding` | R2 — Vectorisation et indexation dans Qdrant      | —    |
| `api`       | R3 — API FastAPI de recherche (RAG)               | 8000 |

```bash
# Construire et monter tous les services
docker compose up --build
```

> ⚠️ Le premier build est long (~2 Go) : `sentence-transformers` télécharge PyTorch.

### 4. Exécuter le pipeline étape par étape (optionnel)

Si vous préférez lancer les étapes individuellement :

```bash
# Démarrer Qdrant seul
docker compose up -d qdrant

# R1 : ingérer le corpus (corpus/raw -> corpus/chunks.jsonl)
docker compose run --rm ingestion

# R2 : vectoriser et indexer les chunks dans Qdrant
docker compose run --rm embedding

# R3 : démarrer l'API
docker compose up -d api

ou 

# pour run tous les containers 
docker compose up 

```



### 5. Tester l'API

```bash
# Vérifier que l'API répond
curl http://localhost:8000/

# Poser une question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Votre question ici"}'
```

Le dashboard Qdrant est accessible sur [http://localhost:6333/dashboard](http://localhost:6333/dashboard).

### Arrêter les services

```bash
docker compose down

# Pour supprimer aussi les données Qdrant
docker compose down -v
```
