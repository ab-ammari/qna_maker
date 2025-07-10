# 🤖 QnA Maker - Système Q&A basé sur RAG
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://qnamaker-agwp5zhkwmstzgasdvbxxa.streamlit.app/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Un système de questions-réponses basé sur la technologie RAG (Retrieval-Augmented Generation) qui vous permet de créer votre propre assistant IA à partir de vos documents personnels.

**🔗 Application déployée: [QnA Maker](https://qnamaker-agwp5zhkwmstzgasdvbxxa.streamlit.app/)**

![Aperçu de l'application](./capture/cap.png)

## ✨ Fonctionnalités
- **📄 Support multi-formats**: Traitement de fichiers PDF, TXT, XLSX et URLs
- **🔍 Recherche sémantique**: Recherche de contenu par similarité vectorielle avec FAISS
- **🧠 Réponses intelligentes**: Génération de réponses contextuelles avec Groq LLM
- **🎤 Interface vocale**: Reconnaissance vocale pour les questions et synthèse vocale pour les réponses
- **🌐 Déploiement facile**: Accessible en ligne via Streamlit Cloud

## 🛠️ Comment ça marche
1. **Importation de documents**: Téléchargez vos fichiers ou entrez des URLs
2. **Traitement du contenu**: Le système divise les documents en chunks et génère des embeddings
3. **Indexation vectorielle**: Les embeddings sont stockés dans une base de données FAISS
4. **Recherche contextuelle**: Vos questions permettent de récupérer les chunks pertinents
5. **Génération de réponses**: Un modèle LLM (via Groq) génère des réponses précises basées sur le contexte

## 🚀 Installation pour développement local
1. **Cloner le dépôt**:
   ```bash
   git clone https://github.com/ab-ammari/qna_maker.git
   cd qnamaker
   ```
2. **Créer un environnement virtuel**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   ```
3. **Installer les dépendances**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configurer la clé API Groq**:
   - Créez un compte sur [Groq](https://console.groq.com)
   - Obtenez votre clé API
   - Créez un fichier `.env` à la racine du projet:
     ```
     GROQ_API_KEY=votre_clé_api_groq
     ```
5. **Lancer l'application**:
   ```bash
   streamlit run app.py
   ```

## 📁 Structure du projet
```
qna_maker/
├── app.py                # Application Streamlit principale
├── requirements.txt      # Dépendances
├── utils/
│   ├── __init__.py
│   ├── document_processor.py  # Traitement des documents
│   ├── embeddings.py          # Gestion des embeddings
│   ├── vector_store.py        # Stockage FAISS
│   ├── llm_handler.py         # Intégration de Groq
│   └── voice_handler.py       # Fonctionnalités vocales
└── data/                 # Dossier pour les données temporaires
    └── .gitkeep
```

## 🔧 Technologies utilisées
- **[Streamlit](https://streamlit.io/)**: Interface utilisateur
- **[LangChain](https://www.langchain.com/)**: Framework pour les applications LLM
- **[FAISS](https://github.com/facebookresearch/faiss)**: Indexation et recherche vectorielle
- **[Hugging Face](https://huggingface.co/)**: Modèles d'embeddings
- **[Groq](https://console.groq.com)**: API pour les modèles LLM (Llama 3, Mixtral)
- **[SpeechRecognition](https://pypi.org/project/SpeechRecognition/)**: Reconnaissance vocale
- **[pyttsx3](https://pypi.org/project/pyttsx3/)**: Synthèse vocale

## 🔮 Améliorations futures
- [ ] Support pour davantage de formats de documents
- [ ] Amélioration de la reconnaissance vocale multilingue
- [ ] Historique des conversations
- [ ] Visualisation des sources avec surlignage du texte pertinent
- [ ] Export des réponses et des sources en PDF
- [ ] Support pour d'autres fournisseurs LLM (OpenAI, Anthropic, etc.)

## 📧 Contact
Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue ou à me contacter directement.

abdelhafid.ammari@outlook.fr

---
*Développé avec ❤️ pour simplifier l'accès à l'information*