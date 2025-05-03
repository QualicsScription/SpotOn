# SpotOn - Advanced File Comparator

SpotOn is a professional file comparison tool designed to compare files in various formats (SolidWorks, CAD, Documents, Images, etc.) with advanced similarity analysis.

## Features
- Compare files based on metadata, hash, content, and structure.
- Visual analysis with pie charts for similarity distribution.
- Detailed analysis with file information and comparison details.
- Multi-language support (English, Turkish).
- Customizable dark theme UI.
- Export results to CSV or HTML reports.

## Installation
1. Navigate to the `Main` directory:
   ```bash
   cd C:\SpotOn\Main
   ```

## Proje Yapısı

- Tüm modüller `src/` dizini altında toplanmıştır:
  - `src/core/`: Karşılaştırma mantığı
  - `src/ui/`: Arayüz bileşenleri
  - `src/resources/`: Renk ve stil tanımları
  - `src/languages/`: Dil dosyaları ve `LanguageManager`

## Kurulum ve Çalıştırma

1. Sanal ortam oluşturun ve etkinleştirin:
   ```powershell
   cd C:\SpotOn\Main
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Bağımlılıkları yükleyin:
   ```powershell
   pip install -r requirements.txt
   ```

3. Uygulamayı çalıştırın:
   ```powershell
   python main.py
   ```

Not: Artık PYTHONPATH ayarına gerek yoktur, çünkü `languages` modülü `src/` altına taşınmıştır.