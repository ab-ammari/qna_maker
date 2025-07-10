"""
Module pour gérer les embeddings avec Hugging Face.
"""
from typing import List, Dict, Any
from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingManager:
    """Classe pour gérer les embeddings avec Hugging Face."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialise le gestionnaire d'embeddings.
        
        Args:
            model_name: Nom du modèle d'embedding Hugging Face
        """
        self.model_name = model_name
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Génère des embeddings pour une liste de textes.
        
        Args:
            texts: Liste de textes à convertir en embeddings
        
        Returns:
            Liste d'embeddings (vecteurs)
        """
        return self.embeddings.embed_documents(texts)
    
    def get_query_embedding(self, query: str) -> List[float]:
        """
        Génère un embedding pour une requête.
        
        Args:
            query: Texte de la requête
        
        Returns:
            Embedding (vecteur) de la requête
        """
        return self.embeddings.embed_query(query)
