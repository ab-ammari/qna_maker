"""
Module pour gérer les fonctionnalités vocales.
"""
import tempfile
import os
import threading
import speech_recognition as sr
import pyttsx3

class VoiceHandler:
    """Classe pour gérer les fonctionnalités de reconnaissance et de synthèse vocale."""
    
    def __init__(self):
        """Initialise le gestionnaire vocal."""
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # Ajuster les propriétés de la voix
        voices = self.engine.getProperty('voices')
        # Tenter de trouver une voix française
        french_voice = None
        for voice in voices:
            if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                french_voice = voice.id
                break
        
        # Définir la voix française si disponible
        if french_voice:
            self.engine.setProperty('voice', french_voice)
        
        # Ajuster la vitesse de parole (valeur par défaut: 200)
        self.engine.setProperty('rate', 180)
    
    def recognize_speech(self, timeout: int = 5) -> str:
        """
        Reconnaît la parole à partir du microphone.
        
        Args:
            timeout: Délai d'attente en secondes
        
        Returns:
            Texte reconnu ou message d'erreur
        """
        with sr.Microphone() as source:
            # Ajuster pour le bruit ambiant
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio, language="fr-FR")
                return text
            except sr.WaitTimeoutError:
                return "Aucune parole détectée. Veuillez réessayer."
            except sr.UnknownValueError:
                return "Désolé, je n'ai pas compris ce que vous avez dit."
            except sr.RequestError:
                return "Le service de reconnaissance vocale n'est pas disponible."
            except Exception as e:
                return f"Erreur lors de la reconnaissance vocale: {str(e)}"
    
    def text_to_speech(self, text: str):
        """
        Convertit le texte en parole.
        
        Args:
            text: Texte à convertir en parole
        """
        # Créer un thread pour la synthèse vocale pour éviter de bloquer l'interface
        def speak_text():
            self.engine.say(text)
            self.engine.runAndWait()
        
        # Lancer la synthèse vocale dans un thread séparé
        threading.Thread(target=speak_text).start()
    
    def save_speech_to_file(self, text: str, file_path: str = None) -> str:
        """
        Sauvegarde la synthèse vocale dans un fichier audio.
        
        Args:
            text: Texte à convertir en parole
            file_path: Chemin du fichier audio (si None, un fichier temporaire est créé)
        
        Returns:
            Chemin du fichier audio créé
        """
        if file_path is None:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp:
                file_path = temp.name
        
        # Sauvegarder la parole dans le fichier
        self.engine.save_to_file(text, file_path)
        self.engine.runAndWait()
        
        return file_path
