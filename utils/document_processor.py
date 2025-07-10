"""
Module pour traiter différents types de documents et les diviser en chunks.
"""
import os
import tempfile
from typing import List, Dict, Any

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
    WebBaseLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """Classe pour traiter divers formats de documents."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialise le processeur de documents.
        
        Args:
            chunk_size: Taille des chunks de texte
            chunk_overlap: Chevauchement entre les chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
    
    def process_file(self, file_obj: Any, file_name: str) -> List[Dict[str, Any]]:
        """
        Traite un fichier téléchargé et retourne des chunks de texte.
        
        Args:
            file_obj: Objet fichier de Streamlit
            file_name: Nom du fichier
        
        Returns:
            Liste de dictionnaires contenant le texte et les métadonnées
        """
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp:
            temp.write(file_obj.getvalue())
            temp_path = temp.name
        
        try:
            # Choisir le chargeur approprié en fonction de l'extension
            ext = os.path.splitext(file_name)[1].lower()
            
            if ext == '.pdf':
                loader = PyPDFLoader(temp_path)
            elif ext == '.txt':
                loader = TextLoader(temp_path)
            elif ext in ['.xlsx', '.xls']:
                loader = UnstructuredExcelLoader(temp_path)
            else:
                raise ValueError(f"Format de fichier non pris en charge: {ext}")
            
            # Charger et diviser le document
            documents = loader.load()
            chunks = self.text_splitter.split_documents(documents)
            
            # Créer une liste de dictionnaires avec texte et métadonnées
            result = []
            for i, chunk in enumerate(chunks):
                result.append({
                    "text": chunk.page_content,
                    "metadata": {
                        "source": file_name,
                        "chunk_id": i,
                        **chunk.metadata
                    }
                })
            
            return result
        
        finally:
            # Nettoyer le fichier temporaire
            os.unlink(temp_path)
    
    def process_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Traite une URL et retourne des chunks de texte.
        
        Args:
            url: URL à traiter
        
        Returns:
            Liste de dictionnaires contenant le texte et les métadonnées
        """
        loader = WebBaseLoader(url)
        documents = loader.load()
        chunks = self.text_splitter.split_documents(documents)
        
        # Créer une liste de dictionnaires avec texte et métadonnées
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                "text": chunk.page_content,
                "metadata": {
                    "source": url,
                    "chunk_id": i,
                    **chunk.metadata
                }
            })
        
        return result
