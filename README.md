# SpotOn - Gelişmiş Dosya Karşılaştırıcı

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-2.1.0--beta-orange.svg)](https://github.com/QualicsScription/SpotOn/releases)
[![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://www.python.org/downloads/)

SpotOn, özellikle SolidWorks dosyaları için optimize edilmiş bir dosya karşılaştırma aracıdır. Dosyalar arasındaki benzerlikleri analiz eder, manipülasyonları tespit eder ve detaylı raporlar sunar. Mühendislik ve tasarım ekipleri için dosya sürümlerini karşılaştırma ve değişiklikleri izleme süreçlerini kolaylaştırır.

![SpotOn Screenshot](https://via.placeholder.com/800x450.png?text=SpotOn+Screenshot)

## 🚀 Özellikler

- **SolidWorks Dosya Desteği**: `.sldprt`, `.sldasm`, `.slddrw` uzantılı dosyalar için özel karşılaştırma algoritmaları
- **Çok Katmanlı Analiz**: Metadata, hash, içerik ve yapı karşılaştırmaları
- **Manipülasyon Tespiti**: Dosyalardaki olası manipülasyonları belirler
- **Detaylı Raporlar**: HTML ve CSV formatlarında raporlar oluşturur
- **Görsel Analiz**: Karşılaştırma sonuçlarını pasta grafiği ile görselleştirir
- **Çoklu Dil Desteği**: Türkçe ve İngilizce arayüz
- **Sıralanabilir Tablolar**: Veri analizini kolaylaştıran sıralama özellikleri

## 📋 Gereksinimler

- Python 3.8 veya üzeri
- PyQt5
- NumPy
- Pandas
- Matplotlib

## 💻 Kurulum

### Depoyu Klonlayın:

```bash
git clone https://github.com/QualicsScription/SpotOn.git
cd SpotOn
```

### Sanal Ortam Oluşturun (Önerilen):

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### Gerekli Bağımlılıkları Yükleyin:

```bash
pip install -r requirements.txt
```

### Uygulamayı Başlatın:

```bash
python Main/main.py
```

## 🔍 Kullanım

1. **Klasör Seçimi**: Analiz etmek istediğiniz dosyaların bulunduğu klasörü seçin
2. **Minimum Benzerlik Eşiği**: Gösterilecek minimum benzerlik yüzdesini ayarlayın
3. **Karşılaştırmayı Başlatın**: "Başlat" butonuna tıklayarak karşılaştırmayı başlatın
4. **Sonuçları İnceleyin**: Tablo görünümü, görsel analiz ve detaylı analiz sekmelerini kullanarak sonuçları inceleyin
5. **Rapor Oluşturma**: Karşılaştırma tamamlandığında, HTML veya CSV formatında raporlar oluşturabilirsiniz

## 📊 Analiz Özellikleri

| Analiz Tipi | Açıklama |
|-------------|----------|
| Metadata | Dosya boyutu, oluşturma tarihi gibi meta verileri karşılaştırır |
| Hash | Dosya içeriğinin kriptografik özeti karşılaştırılır |
| İçerik | Dosya içeriğinin yapısal olmayan kısımları karşılaştırılır |
| Yapı | Dosya yapısı ve organizasyonu karşılaştırılır |
| Manipülasyon | Dosyalarda yapılmış olabilecek kasıtlı değişiklikler tespit edilir |

## 🌐 Desteklenen Dosya Tipleri

- **SolidWorks**: `.sldprt`, `.sldasm`, `.slddrw`
- **CAD**: `.step`, `.stp`, `.iges`, `.igs`, `.stl`, `.obj`, `.dxf`
- **Döküman**: `.docx`, `.xlsx`, `.pdf`, `.txt`
- **Görsel**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tif`, `.tiff`

## 🔄 Sürüm Geçmişi

- **2.1.0-beta**: Geliştirilmiş UI ve dil desteği
- **2.0.0-alpha**: Temel işlevselliğe sahip ilk sürüm

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen şu adımları izleyin:

1. Bu depoyu fork edin
2. Yeni bir özellik dalı oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Dalınıza push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## 📜 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

Mehmet Zahit Nayir - [@QualicsScription](https://github.com/QualicsScription)

Proje Linki: [https://github.com/QualicsScription/SpotOn](https://github.com/QualicsScription/SpotOn)

---

<p align="center">
  <b>SpotOn - Dosya karşılaştırmada yeni bir standart.</b>
</p>
