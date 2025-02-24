import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import time
import playsound
import hashlib
from pathlib import Path

class RealTimeTranslator:
    def __init__(self, source_lang='en', target_lang='fr'):
        print("Initializing translator...")
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Validate language codes before initializing
        try:
            self.translator = GoogleTranslator(source=source_lang, target=target_lang)
            # Test translation to verify languages are supported
            self.translator.translate("test")
        except Exception as e:
            raise ValueError(f"Failed to initialize translator: {str(e)}")
        
        self.recognizer = sr.Recognizer()
        self.cache_dir = Path("translation_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.translation_cache = {}
        
        # Set some reasonable defaults for speech recognition
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("Initialization complete!")

    def get_audio_filename(self, text):
        """Generate a unique filename for the audio based on text content"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return self.cache_dir / f"audio_{self.target_lang}_{text_hash}.mp3"

    def listen_and_translate(self):
        """Listen to audio input and translate in real-time"""
        try:
            with sr.Microphone() as source:
                self.adjust_for_ambient_noise(source)
                print(f"\nListening... (Speak in {self.source_lang})")
                print("Press Ctrl+C to stop")
                
                while True:
                    try:
                        # Listen for audio input with a timeout
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        
                        # Convert speech to text
                        print("\nProcessing speech...", end='\r')
                        text = self.recognizer.recognize_google(audio, language=self.source_lang)
                        print(f"\nYou said: {text}")
                        
                        # Rate limit check to prevent API abuse
                        time.sleep(0.5)
                        
                        # Translation with progress feedback
                        if text in self.translation_cache:
                            translation = self.translation_cache[text]
                            print(f"Translation (cached): {translation}")
                        else:
                            print("Translating...", end='\r')
                            translation = self.translator.translate(text)
                            self.translation_cache[text] = translation
                            print(f"Translation: {translation}")
                        
                        self.text_to_speech(translation)
                        
                    except sr.WaitTimeoutError:
                        print(".", end='', flush=True)  # Show activity while waiting
                        continue
                    except sr.UnknownValueError:
                        print("\nCould not understand audio. Please try again.")
                    except sr.RequestError as e:
                        print(f"\nError with speech recognition service: {e}")
                    except Exception as e:
                        print(f"\nUnexpected error: {str(e)}")
                        time.sleep(1)  # Prevent rapid error loops
                        
        except KeyboardInterrupt:
            print("\nTranslation stopped by user.")
        finally:
            self.cleanup()

    def text_to_speech(self, text, max_retries=3):
        """Convert text to speech and play it with retry logic"""
        for attempt in range(max_retries):
            try:
                audio_file = self.get_audio_filename(text)
                
                if not audio_file.exists():
                    print("Generating audio...", end='\r')
                    tts = gTTS(text=text, lang=self.target_lang)
                    tts.save(str(audio_file))
                
                playsound.playsound(str(audio_file))
                return
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"\nFailed to process text-to-speech after {max_retries} attempts: {str(e)}")
                else:
                    print(f"\nRetrying text-to-speech (attempt {attempt + 2}/{max_retries})")
                    time.sleep(1)

    def cleanup(self):
        """Clean up old cache files"""
        # Keep only files newer than 24 hours
        current_time = time.time()
        for file in self.cache_dir.glob("*.mp3"):
            if current_time - file.stat().st_mtime > 86400:  # 24 hours
                try:
                    file.unlink()
                except Exception:
                    pass

    def adjust_for_ambient_noise(self, source):
        """Adjust microphone for ambient noise with progress indication"""
        print("\nAdjusting for ambient noise... Please wait...")
        try:
            for i in range(3):
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Calibrating... {i+1}/3")
            print("Ambient noise adjustment complete!")
        except Exception as e:
            print(f"Warning: Could not adjust for ambient noise: {str(e)}")

    def manage_cache(self, max_cache_size=1000):
        """Manage the translation cache size"""
        if len(self.translation_cache) > max_cache_size:
            # Remove oldest 20% of entries
            items_to_remove = int(max_cache_size * 0.2)
            for _ in range(items_to_remove):
                self.translation_cache.pop(next(iter(self.translation_cache)))

def main():
    # Available languages with their native names
    languages = {
        'en': 'English (English)',
        'fr': 'French (Français)',
        'es': 'Spanish (Español)',
        'de': 'German (Deutsch)',
        'it': 'Italian (Italiano)',
        'pt': 'Portuguese (Português)',
        'ru': 'Russian (Русский)',
        'ja': 'Japanese (日本語)',
        'ko': 'Korean (한국어)',
        'zh': 'Chinese (中文)'
    }
    
    print("\n=== Real-Time Language Translator ===")
    print("\nAvailable languages:")
    for code, name in languages.items():
        print(f"{code}: {name}")
    
    def get_language_input(prompt, default):
        while True:
            lang = input(prompt).lower() or default
            if lang in languages:
                return lang
            print(f"Invalid language code. Please choose from: {', '.join(languages.keys())}")
    
    source_lang = get_language_input("\nEnter source language code (default 'en'): ", 'en')
    target_lang = get_language_input("Enter target language code (default 'fr'): ", 'fr')
    
    print(f"\nTranslating from {languages[source_lang]} to {languages[target_lang]}")
    
    try:
        translator = RealTimeTranslator(source_lang=source_lang, target_lang=target_lang)
        translator.listen_and_translate()
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please check your language selections and try again.")

if __name__ == "__main__":
    main() 

I want to do streamlit community deployment of this code.
generate the necessary codes and files
