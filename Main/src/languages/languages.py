class LanguageManager:
    def __init__(self):
        # Basit bir çeviri sözlüğü
        self.translations = {
            "hello": {"en": "Hello", "tr": "Merhaba"},
            "app_title": {"en": "Advanced File Comparator", "tr": "Gelişmiş Dosya Karşılaştırıcı"},
            "select_file_1": {"en": "Select File 1", "tr": "Dosya 1 Seç"},
            "select_file_2": {"en": "Select File 2", "tr": "Dosya 2 Seç"},
            "compare": {"en": "Compare", "tr": "Karşılaştır"},
            "no_file_selected": {"en": "No file selected", "tr": "Dosya seçilmedi"}
        }
        self.current_language = "en"  # Varsayılan dil

    def set_language(self, language):
        if language in ["en", "tr"]:
            self.current_language = language

    def translate(self, key):
        return self.translations.get(key, {}).get(self.current_language, key)