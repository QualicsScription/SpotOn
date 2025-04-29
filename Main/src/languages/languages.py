import os
import json
from PyQt5.QtCore import QSettings

class LanguageManager:
    def __init__(self):
        self.settings = QSettings("SpotOn", "AdvancedFileComparator")
        self.current_lang = self.settings.value("language", "en")
        self.lang_dir = "languages"
        self.languages = {
            "en": os.path.join(self.lang_dir, "en.json"),
            "tr": os.path.join(self.lang_dir, "tr.json")
        }
        self.default_translations = {
            "en": {
                "title": "Advanced File Comparator",
                "folder": "Folder:",
                "browse": "Browse",
                "solidworks": "SolidWorks",
                "cad": "CAD",
                "document": "Document",
                "image": "Image",
                "all_files": "All Files",
                "min_similarity": "Min. Similarity:",
                "status_ready": "Ready",
                "status_running": "Running...",
                "status_stopped": "Stopped",
                "start": "Start",
                "stop": "Stop",
                "clear": "Clear",
                "report": "Report",
                "csv": "CSV",
                "help": "Help",
                "table_view": "Table View",
                "visual_analysis": "Visual Analysis",
                "detailed_analysis": "Detailed Analysis",
                "file1": "File 1",
                "file2": "File 2",
                "metadata": "Metadata",
                "hash": "Hash",
                "content": "Content",
                "structure": "Structure",
                "total": "Total",
                "result": "Result",
                "invalid_folder": "Please select a valid folder!",
                "completed": "Completed!",
                "similar_files_found": "similar file pairs found.",
                "similarity_stats": "SIMILARITY STATISTICS",
                "total_comparisons": "Total Comparisons",
                "average_similarity": "Average Similarity",
                "maximum": "Maximum",
                "minimum": "Minimum",
                "detailed_comparison": "Detailed Comparison",
                "total_similarity": "Total Similarity",
                "file_type": "File Type",
                "weighted_scores": "Weighted Scores",
                "manipulation_analysis": "Manipulation Analysis",
                "detection": "Detection",
                "score": "Score",
                "type": "Type",
                "solidworks_detailed_analysis": "SolidWorks Detailed Analysis",
                "feature_tree": "Feature Tree",
                "sketch_data": "Sketch Data",
                "geometry": "Geometry",
                "no_results_for_report": "No results to generate a report!",
                "no_results_to_export": "No results to export!",
                "save_report": "Save Report",
                "save_csv": "Save CSV",
                "results_exported": "Results successfully exported to:",
                "usage_instructions": "Usage:\n1. Select a folder\n2. Choose file type\n3. Set minimum similarity threshold\n4. Click Start"
            },
            "tr": {
                "title": "Gelişmiş Dosya Karşılaştırıcı",
                "folder": "Klasör:",
                "browse": "Gözat",
                "solidworks": "SolidWorks",
                "cad": "CAD",
                "document": "Döküman",
                "image": "Görsel",
                "all_files": "Tüm Dosyalar",
                "min_similarity": "Min. Benzerlik:",
                "status_ready": "Hazır",
                "status_running": "Çalışıyor...",
                "status_stopped": "Durduruldu",
                "start": "Başlat",
                "stop": "Durdur",
                "clear": "Temizle",
                "report": "Rapor",
                "csv": "CSV",
                "help": "Yardım",
                "table_view": "Tablo Görünümü",
                "visual_analysis": "Görsel Analiz",
                "detailed_analysis": "Detaylı Analiz",
                "file1": "Dosya 1",
                "file2": "Dosya 2",
                "metadata": "Metadata",
                "hash": "Hash",
                "content": "İçerik",
                "structure": "Yapı",
                "total": "Toplam",
                "result": "Sonuç",
                "invalid_folder": "Geçerli bir klasör seçin!",
                "completed": "Tamamlandı!",
                "similar_files_found": "benzer dosya çifti bulundu.",
                "similarity_stats": "BENZERLIK İSTATISTIKLERI",
                "total_comparisons": "Toplam Karşılaştırma",
                "average_similarity": "Ortalama Benzerlik",
                "maximum": "Maksimum",
                "minimum": "Minimum",
                "detailed_comparison": "Detaylı Karşılaştırma",
                "total_similarity": "Toplam Benzerlik",
                "file_type": "Dosya Tipi",
                "weighted_scores": "Ağırlıklı Skorlar",
                "manipulation_analysis": "Manipülasyon Analizi",
                "detection": "Tespit",
                "score": "Skor",
                "type": "Tür",
                "solidworks_detailed_analysis": "SolidWorks Detaylı Analiz",
                "feature_tree": "Feature Tree",
                "sketch_data": "Sketch Data",
                "geometry": "Geometri",
                "no_results_for_report": "Rapor oluşturmak için sonuç bulunmuyor!",
                "no_results_to_export": "Dışa aktarmak için sonuç bulunmuyor!",
                "save_report": "Rapor Dosyasını Kaydet",
                "save_csv": "CSV Dosyasını Kaydet",
                "results_exported": "Sonuçlar başarıyla dışa aktarıldı:",
                "usage_instructions": "Kullanım:\n1. Klasör seçin\n2. Dosya tipini belirleyin\n3. Minimum benzerlik eşiğini ayarlayın\n4. Başlat butonuna tıklayın"
            }
        }
        if not os.path.exists(self.lang_dir):
            os.makedirs(self.lang_dir)
        for lang, file_path in self.languages.items():
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.default_translations[lang], f, ensure_ascii=False, indent=4)
        self.translations = self.load_translations()

    def load_translations(self):
        with open(self.languages[self.current_lang], 'r', encoding='utf-8') as f:
            return json.load(f)

    def set_language(self, lang):
        self.current_lang = lang
        self.settings.setValue("language", lang)
        self.translations = self.load_translations()

    def translate(self, key):
        return self.translations.get(key, key)