"""
Application principale Streamlit pour le système Q&A basé sur RAG.
"""
import os
import time
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Importer les modules d'utilitaires
from utils import (
    DocumentProcessor,
    EmbeddingManager,
    VectorStore,
    LLMHandler,
    VoiceHandler
)

# Constantes
DATA_DIR = "data"
VECTOR_STORE_NAME = "vector_store"

# Initialiser les variables de session
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.vector_store = None
    st.session_state.document_processor = None
    st.session_state.embedding_manager = None
    st.session_state.llm_handler = None
    st.session_state.voice_handler = None
    st.session_state.documents = []
    st.session_state.processing = False
    st.session_state.last_query = ""
    st.session_state.last_response = ""

def initialize_components():
    """Initialise tous les composants nécessaires."""
    if not st.session_state.initialized:
        try:
            # Créer le répertoire de données s'il n'existe pas
            os.makedirs(DATA_DIR, exist_ok=True)
            
            # Initialiser les composants
            st.session_state.document_processor = DocumentProcessor()
            st.session_state.embedding_manager = EmbeddingManager()
            st.session_state.vector_store = VectorStore()
            
            # Tenter de charger un vector store existant
            if st.session_state.vector_store.load(DATA_DIR, VECTOR_STORE_NAME):
                st.info("Base de connaissances précédente chargée avec succès.")
            
            # Initialiser le gestionnaire LLM si la clé API est disponible
            api_key = os.environ.get("GROQ_API_KEY")
            if api_key:
                st.session_state.llm_handler = LLMHandler(api_key=api_key)
            
            # Initialiser le gestionnaire vocal
            st.session_state.voice_handler = VoiceHandler()
            
            st.session_state.initialized = True
            return True
        except Exception as e:
            st.error(f"Erreur lors de l'initialisation: {str(e)}")
            return False
    return True

def process_documents(files, urls):
    """Traite les documents et les URLs."""
    st.session_state.processing = True
    processed_docs = []
    
    with st.spinner("Traitement des documents..."):
        # Traiter les fichiers
        for file in files:
            try:
                chunks = st.session_state.document_processor.process_file(file, file.name)
                processed_docs.extend(chunks)
                st.info(f"✅ {file.name} traité avec succès ({len(chunks)} chunks)")
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de {file.name}: {str(e)}")
        
        # Traiter les URLs
        for url in urls:
            try:
                chunks = st.session_state.document_processor.process_url(url)
                processed_docs.extend(chunks)
                st.info(f"✅ {url} traité avec succès ({len(chunks)} chunks)")
            except Exception as e:
                st.error(f"❌ Erreur lors du traitement de {url}: {str(e)}")
    
    # Calculer les embeddings et ajouter au vector store
    if processed_docs:
        with st.spinner("Calcul des embeddings et mise à jour de la base de connaissances..."):
            texts = [doc["text"] for doc in processed_docs]
            embeddings = st.session_state.embedding_manager.get_embeddings(texts)
            st.session_state.vector_store.add_documents(processed_docs, embeddings)
            
            # Sauvegarder le vector store
            st.session_state.vector_store.save(DATA_DIR, VECTOR_STORE_NAME)
            
            # Mettre à jour la session
            st.session_state.documents.extend(processed_docs)
            st.success(f"✅ {len(processed_docs)} chunks ajoutés à la base de connaissances.")
    
    st.session_state.processing = False

def generate_response(query):
    """Génère une réponse à la requête."""
    if not query:
        return "Veuillez entrer une question."
    
    if not st.session_state.vector_store or not st.session_state.llm_handler:
        return "Le système n'est pas complètement initialisé. Veuillez vérifier vos clés API et réessayer."
    
    # Obtenir l'embedding de la requête
    query_embedding = st.session_state.embedding_manager.get_query_embedding(query)
    
    # Rechercher les documents pertinents
    relevant_docs = st.session_state.vector_store.similarity_search(query_embedding, k=4)
    
    if not relevant_docs:
        return "Je n'ai pas trouvé d'informations pertinentes dans les documents fournis. Veuillez essayer une autre question ou ajouter plus de documents."
    
    # Générer la réponse avec le LLM
    response = st.session_state.llm_handler.get_response(query, relevant_docs)
    
    # Mettre à jour la session
    st.session_state.last_query = query
    st.session_state.last_response = response
    
    return response

def main():
    """Fonction principale de l'application."""
    st.set_page_config(
        page_title="Q&A RAG System",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Système Q&A basé sur RAG")
    st.markdown("""
    Bienvenue dans ce système de questions-réponses basé sur RAG (Retrieval-Augmented Generation).
    Téléchargez vos documents ou entrez des URLs pour créer votre base de connaissances personnalisée.
    """)
    
    # Vérifier la clé API Groq
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        api_key = st.text_input("Veuillez entrer votre clé API Groq", type="password")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.success("Clé API Groq enregistrée avec succès.")
            if not st.session_state.llm_handler and st.session_state.initialized:
                st.session_state.llm_handler = LLMHandler(api_key=api_key)
            st.experimental_rerun()
    
    # Initialiser les composants
    if not initialize_components():
        st.stop()
    
    # Interface à onglets
    tab1, tab2, tab3 = st.tabs(["📚 Documents", "❓ Questions & Réponses", "ℹ️ À propos"])
    
    # Onglet Documents
    with tab1:
        st.header("📚 Gestion des Documents")
        
        # Upload de fichiers
        st.subheader("Télécharger des fichiers")
        uploaded_files = st.file_uploader(
            "Téléchargez des fichiers (PDF, TXT, XLSX)",
            accept_multiple_files=True,
            type=["pdf", "txt", "xlsx", "xls"]
        )
        
        # Entrée d'URL
        st.subheader("Ajouter des URLs")
        url_input = st.text_area("Entrez des URLs (une par ligne)")
        urls = [url.strip() for url in url_input.split("\n") if url.strip()]
        
        # Bouton de traitement
        if st.button("Traiter les documents", disabled=st.session_state.processing):
            if not uploaded_files and not urls:
                st.warning("Veuillez télécharger au moins un fichier ou entrer une URL.")
            else:
                process_documents(uploaded_files, urls)
        
        # Afficher les statistiques
        if st.session_state.documents:
            st.subheader("Statistiques de la base de connaissances")
            
            # Nombre total de documents et de chunks
            sources = set()
            for doc in st.session_state.documents:
                sources.add(doc["metadata"]["source"])
            
            st.metric("Documents sources", len(sources))
            st.metric("Chunks de texte", len(st.session_state.documents))
            
            # Liste des sources
            st.subheader("Sources de données")
            source_list = list(sources)
            for source in source_list:
                st.write(f"- {source}")
        
        # Bouton pour réinitialiser la base de connaissances
        if st.session_state.documents and st.button("Réinitialiser la base de connaissances"):
            st.session_state.vector_store = VectorStore()
            st.session_state.documents = []
            
            # Supprimer les fichiers du vector store
            index_path = os.path.join(DATA_DIR, f"{VECTOR_STORE_NAME}.index")
            docs_path = os.path.join(DATA_DIR, f"{VECTOR_STORE_NAME}.pkl")
            
            if os.path.exists(index_path):
                os.remove(index_path)
            if os.path.exists(docs_path):
                os.remove(docs_path)
            
            st.success("Base de connaissances réinitialisée avec succès.")
            st.experimental_rerun()
    
    # Onglet Questions & Réponses
    with tab2:
        st.header("❓ Questions & Réponses")
        
        # Vérifier si des documents sont chargés
        if not st.session_state.documents:
            st.warning("Veuillez d'abord ajouter des documents dans l'onglet 'Documents'.")
            st.stop()
        
        # Interface de question
        st.subheader("Posez votre question")
        
        # Option vocale
        voice_col1, voice_col2 = st.columns([3, 1])
        with voice_col1:
            query = st.text_input("Entrez votre question", key="query_input")
        with voice_col2:
            if st.button("🎤 Parler", key="voice_button"):
                with st.spinner("Écoute en cours..."):
                    voice_input = st.session_state.voice_handler.recognize_speech()
                    if not voice_input.startswith("Erreur") and not voice_input.startswith("Aucune") and not voice_input.startswith("Désolé"):
                        st.session_state.query_input = voice_input
                        query = voice_input
                        st.experimental_rerun()
                    else:
                        st.error(voice_input)
        
        # Bouton de soumission
        if st.button("Obtenir une réponse", disabled=not query):
            with st.spinner("Génération de la réponse en cours..."):
                response = generate_response(query)
                st.session_state.last_response = response
        
        # Afficher la réponse
        if st.session_state.last_query and st.session_state.last_response:
            st.subheader("Réponse")
            st.info(f"Question: {st.session_state.last_query}")
            st.write(st.session_state.last_response)
            
            # Option pour lire la réponse à haute voix
            if st.button("🔊 Lire la réponse"):
                st.session_state.voice_handler.text_to_speech(st.session_state.last_response)
    
    # Onglet À propos
    with tab3:
        st.header("ℹ️ À propos de ce système")
        st.markdown("""
        ### Q&A RAG System
        
        Ce système utilise l'approche RAG (Retrieval-Augmented Generation) pour créer un assistant de questions-réponses personnalisé qui s'appuie sur vos propres documents.
        
        #### Technologies utilisées :
        - **Document Processing** : LangChain pour traiter divers formats de documents
        - **Embeddings** : Hugging Face pour la génération d'embeddings (gratuit et open-source)
        - **Vector Storage** : FAISS (Facebook AI Similarity Search) pour l'indexation et la recherche vectorielle
        - **LLM** : API Groq pour la génération de réponses (utilisant des modèles comme Llama 3 ou Mixtral)
        - **Interface** : Streamlit pour l'interface utilisateur
        - **Vocal** : Fonctionnalités de reconnaissance et de synthèse vocale
        
        #### Comment ça marche :
        1. **Téléchargez vos documents** : PDF, TXT, XLSX ou entrez des URLs
        2. **Le système traite et indexe** : Les documents sont divisés en chunks, transformés en vecteurs et indexés
        3. **Posez vos questions** : Le système recherche les informations pertinentes dans vos documents
        4. **Obtenez des réponses précises** : Les réponses sont générées à partir du contexte trouvé
        
        #### Avantages :
        - **Personnalisé** : Répond aux questions basées sur VOS documents
        - **Précis** : Les réponses sont ancrées dans le contexte fourni, réduisant les hallucinations
        - **Gratuit** : Utilise principalement des outils open-source (seule l'API Groq nécessite un compte)
        - **Multimodal** : Supporte la voix et le texte
        """)

if __name__ == "__main__":
    main()
