# Main/languages/languages.py
import json
import os
from PyQt5.QtCore import QSettings

class LanguageManager:
    def __init__(self):
        self.settings = QSettings("SpotOn", "Language")
        self.current_language = self.settings.value("language", "tr")
        self.translations = self.load_translations()

    def load_translations(self):
        languages_dir = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(os.path.join(languages_dir, f"{self.current_language}.json"), 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Dil dosyası yüklenemedi: {e}")
            return {}

    def set_language(self, lang):
        self.current_language = lang
        self.settings.setValue("language", lang)
        self.translations = self.load_translations()

    def translate(self, key):
        return self.translations.get(key, key)