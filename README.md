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

## 🛠️ Prérequis

Avant de lancer le projet, assurez-vous de disposer des éléments suivants :
*   **Docker** et **Docker Compose** (pour conteneuriser et lancer les services comme Qdrant).
*   **Python 3.x** (pour exécuter les scripts d'ingestion et d'embedding).
*   Un environnement virtuel Python configuré avec les dépendances installées.

## 🚀 Installation et Lancement

1. **Cloner le dépôt :**
```bash
   git clone git@github.com:NassJs/BAMN-TP.git
   cd BAMN-TP
```
