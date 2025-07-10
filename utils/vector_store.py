"""
Module pour gérer le stockage vectoriel avec FAISS.
"""
import os
import pickle
from typing import List, Dict, Any, Optional
import numpy as np
import faiss

class VectorStore:
    """Classe pour gérer le stockage et la recherche vectorielle avec FAISS."""
    
    def __init__(self, dimension: int = 384):
        """
        Initialise le stockage vectoriel.
        
        Args:
            dimension: Dimension des vecteurs d'embedding
        """
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []  # Stocke les documents originaux
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Ajoute des documents et leurs embeddings à l'index.
        
        Args:
            documents: Liste de dictionnaires contenant le texte et les métadonnées
            embeddings: Liste des embeddings correspondants
        """
        if not documents:
            return
        
        # Convertir les embeddings en format numpy
        embeddings_np = np.array(embeddings).astype('float32')
        
        # Ajouter à l'index FAISS
        self.index.add(embeddings_np)
        
        # Stocker les documents originaux
        self.documents.extend(documents)
    
    def similarity_search(self, query_embedding: List[float], k: int = 4) -> List[Dict[str, Any]]:
        """
        Recherche les documents les plus similaires à la requête.
        
        Args:
            query_embedding: Embedding de la requête
            k: Nombre de résultats à retourner
        
        Returns:
            Liste des documents les plus pertinents
        """
        if len(self.documents) == 0:
            return []
        
        # Convertir l'embedding de requête en format numpy
        query_embedding_np = np.array([query_embedding]).astype('float32')
        
        # Effectuer la recherche
        distances, indices = self.index.search(query_embedding_np, min(k, len(self.documents)))
        
        # Récupérer les documents correspondants
        results = []
        for idx in indices[0]:
            if idx != -1 and idx < len(self.documents):
                results.append(self.documents[idx])
        
        return results
    
    def save(self, directory: str, name: str = "vector_store"):
        """
        Sauvegarde l'index et les documents.
        
        Args:
            directory: Répertoire où sauvegarder les fichiers
            name: Nom de base pour les fichiers
        """
        os.makedirs(directory, exist_ok=True)
        
        # Sauvegarder l'index FAISS
        index_path = os.path.join(directory, f"{name}.index")
        faiss.write_index(self.index, index_path)
        
        # Sauvegarder les documents
        docs_path = os.path.join(directory, f"{name}.pkl")
        with open(docs_path, 'wb') as f:
            pickle.dump(self.documents, f)
    
    def load(self, directory: str, name: str = "vector_store") -> bool:
        """
        Charge l'index et les documents.
        
        Args:
            directory: Répertoire contenant les fichiers
            name: Nom de base des fichiers
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        index_path = os.path.join(directory, f"{name}.index")
        docs_path = os.path.join(directory, f"{name}.pkl")
        
        if not os.path.exists(index_path) or not os.path.exists(docs_path):
            return False
        
        try:
            # Charger l'index FAISS
            self.index = faiss.read_index(index_path)
            
            # Charger les documents
            with open(docs_path, 'rb') as f:
                self.documents = pickle.load(f)
            
            return True
        except Exception:
            return False
