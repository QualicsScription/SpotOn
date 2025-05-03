import json
import os

class LanguageManager:
    def __init__(self):
        self.translations = {}
        self.current_lang = "tr"  # Varsayılan dil Türkçe
        self.load_translations()

    def load_translations(self):
        try:
            # Önce mevcut dizinde (src/languages) arama yap
            current_dir = os.path.dirname(os.path.abspath(__file__))
            lang_file = os.path.join(current_dir, f"{self.current_lang}.json")

            if os.path.exists(lang_file):
                with open(lang_file, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            else:
                print(f"Dil dosyası bulunamadı: {lang_file}")
                self.translations = {}
        except Exception as e:
            print(f"Dil dosyası yüklenemedi: {e}")
            self.translations = {}

    def set_language(self, lang_code):
        self.current_lang = lang_code
        self.load_translations()

    def translate(self, key):
        return self.translations.get(key, key)