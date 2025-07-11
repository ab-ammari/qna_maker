"""
Module pour gérer l'intégration avec Groq LLM.
"""
from typing import List, Dict, Any
import os
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

class LLMHandler:
    """Classe pour gérer les interactions avec le LLM via Groq."""
    
    def __init__(self, api_key: str = None, model_name: str = "llama-4-scout-17b-16e-instruct"):
        """
        Initialise le gestionnaire LLM.
        
        Args:
            api_key: Clé API Groq (si None, tente de la récupérer depuis les variables d'environnement)
            model_name: Nom du modèle à utiliser (par défaut llama3-8b-8192)
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Clé API Groq non fournie. Définissez GROQ_API_KEY dans les variables d'environnement ou passez-la en paramètre.")
        
        self.model_name = model_name
        self.llm = ChatGroq(
            api_key=self.api_key,
            model_name=self.model_name
        )
        
        # Créer le template de prompt
        self.prompt_template = ChatPromptTemplate.from_template(
            """Vous êtes un assistant IA utile qui répond aux questions en utilisant uniquement 
            le contexte fourni. Si la réponse n'est pas dans le contexte, dites simplement que 
            vous ne savez pas. Ne faites pas référence au contexte dans votre réponse. 
            Citez les sources lorsque cela est possible.
            
            Contexte:
            {context}
            
            Question: {question}
            
            Réponse:"""
        )
        
        # Créer la chaîne LLM
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )
    
    def get_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """
        Génère une réponse à partir de la requête et du contexte.
        
        Args:
            query: Requête de l'utilisateur
            context_docs: Documents de contexte pertinents
        
        Returns:
            Réponse générée par le LLM
        """
        # Formater le contexte
        context_text = "\n\n".join([
            f"Source: {doc['metadata']['source']}\n{doc['text']}"
            for doc in context_docs
        ])
        
        # Si aucun contexte n'est fourni
        if not context_text:
            context_text = "Aucune information pertinente trouvée."
        
        # Invoquer la chaîne LLM
        response = self.chain.invoke({
            "question": query,
            "context": context_text
        })
        
        return response["text"]
