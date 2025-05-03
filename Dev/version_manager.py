#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SpotOn Version Manager

Bu araç, SpotOn projesinin versiyonlarını yönetmek için kullanılır.
- Mevcut sürümü yedekler
- Yeni sürüm için gerekli değişiklikleri yapar
- Sürüm geçişlerini otomatikleştirir
"""

import os
import sys
import shutil
import datetime
import re
import json
from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAIN_DIR = PROJECT_ROOT / "Main"
OLD_DIR = PROJECT_ROOT / "Old"

# Sürüm tipleri
VERSION_TYPES = ["alpha", "beta", "release"]

def get_current_version():
    """
    ui.py dosyasından mevcut sürüm numarasını alır.
    """
    ui_path = MAIN_DIR / "src" / "ui" / "ui.py"
    if not ui_path.exists():
        return None, None
    
    with open(ui_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Sürüm numarasını bul
    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not version_match:
        return None, None
    
    version_str = version_match.group(1)
    
    # Sürüm tipini belirle (alpha, beta, release)
    if "alpha" in version_str.lower():
        version_type = "alpha"
    elif "beta" in version_str.lower():
        version_type = "beta"
    else:
        version_type = "release"
    
    # Sürüm numarasını ayıkla (örn: 2.0.0-alpha -> 2.0.0)
    version_number = re.sub(r'[-](alpha|beta|rc).*$', '', version_str, flags=re.IGNORECASE)
    
    return version_str, version_type

def parse_version(version_str):
    """
    Sürüm numarasını parçalara ayırır.
    Örnek: "2.1.0-beta" -> (2, 1, 0, "beta")
    """
    # Sürüm numarasını ve tipini ayır
    match = re.match(r'(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z]+))?', version_str)
    if not match:
        return None
    
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    version_type = match.group(4) if match.group(4) else "release"
    
    return major, minor, patch, version_type.lower()

def get_next_version(current_version, target_type=None, increment_level=None):
    """
    Mevcut sürüme göre bir sonraki sürümü belirler.
    
    Args:
        current_version: Mevcut sürüm numarası (örn: "2.1.0-beta")
        target_type: Hedef sürüm tipi (alpha, beta, release)
        increment_level: Artırılacak seviye (major, minor, patch)
    
    Returns:
        Bir sonraki sürüm numarası
    """
    if not current_version:
        return "1.0.0-alpha"
    
    parsed = parse_version(current_version)
    if not parsed:
        return "1.0.0-alpha"
    
    major, minor, patch, current_type = parsed
    
    # Eğer hedef tip belirtilmemişse, mevcut tipi kullan
    if not target_type:
        target_type = current_type
    
    # Eğer aynı tip içinde ilerliyorsak (örn: alpha -> alpha)
    if target_type == current_type:
        if increment_level == "major":
            return f"{major+1}.0.0-{target_type}"
        elif increment_level == "minor":
            return f"{major}.{minor+1}.0-{target_type}"
        else:  # patch
            return f"{major}.{minor}.{patch+1}-{target_type}"
    
    # Eğer farklı bir tipe geçiyorsak (örn: alpha -> beta)
    type_index_current = VERSION_TYPES.index(current_type) if current_type in VERSION_TYPES else -1
    type_index_target = VERSION_TYPES.index(target_type) if target_type in VERSION_TYPES else -1
    
    # Eğer daha ileri bir tipe geçiyorsak (örn: alpha -> beta)
    if type_index_target > type_index_current:
        if target_type == "release":
            return f"{major}.{minor}.{patch}"
        else:
            return f"{major}.{minor}.{patch}-{target_type}"
    
    # Eğer daha geri bir tipe geçiyorsak (örn: beta -> alpha)
    # Bu durumda minor sürümü artırıyoruz
    return f"{major}.{minor+1}.0-{target_type}"

def copy_directory(src, dest):
    """
    Bir dizini ve içeriğini başka bir dizine kopyalar.
    """
    if not os.path.exists(dest):
        os.makedirs(dest)
    
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dest, item)
        
        if os.path.isdir(s):
            copy_directory(s, d)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime > os.stat(d).st_mtime:
                shutil.copy2(s, d)

def backup_current_version(version_str, version_type):
    """
    Mevcut sürümü Old klasörüne yedekler.
    """
    if not version_str or not version_type:
        print("Hata: Mevcut sürüm bilgisi alınamadı.")
        return False
    
    # Yedek klasörünü oluştur
    backup_dir = OLD_DIR / f"{version_type}_{version_str.replace('.', '_').replace('-', '_')}"
    if backup_dir.exists():
        print(f"Uyarı: {backup_dir} zaten mevcut. Üzerine yazılacak.")
    
    # Kopyalama işlemi
    try:
        print(f"Mevcut sürüm {MAIN_DIR} dizininden {backup_dir} dizinine kopyalanıyor...")
        copy_directory(MAIN_DIR, backup_dir)
        print(f"Kopyalama işlemi başarıyla tamamlandı!")
        return True
    except Exception as e:
        print(f"Kopyalama sırasında hata oluştu: {e}")
        return False

def update_version_in_files(new_version, new_type):
    """
    Dosyalardaki sürüm numaralarını günceller.
    """
    # ui.py dosyasını güncelle
    ui_path = MAIN_DIR / "src" / "ui" / "ui.py"
    if ui_path.exists():
        with open(ui_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Sürüm numarasını güncelle
        new_content = re.sub(
            r'__version__\s*=\s*["\']([^"\']+)["\']',
            f'__version__ = "{new_version}"',
            content
        )
        
        with open(ui_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"ui.py dosyasındaki sürüm numarası {new_version} olarak güncellendi.")
    
    # README.md dosyasını güncelle
    readme_path = MAIN_DIR / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Başlıktaki sürüm numarasını güncelle
        if new_type == "release":
            title_replacement = f"# SpotOn - Advanced File Comparator (v{new_version})"
        else:
            title_replacement = f"# SpotOn - Advanced File Comparator ({new_type.capitalize()} {new_version})"
        
        new_content = re.sub(
            r'# SpotOn - Advanced File Comparator.*',
            title_replacement,
            content
        )
        
        # Sürüm geçmişini güncelle
        version_history_pattern = r'## Version History\s*\n(.*?\n)*?(?=##|$)'
        version_history_match = re.search(version_history_pattern, new_content, re.DOTALL)
        
        if version_history_match:
            version_history = version_history_match.group(0)
            # Yeni sürümü ekle
            if new_type == "release":
                new_version_entry = f"- **{new_version}**: Current release version\n"
            else:
                new_version_entry = f"- **{new_version}**: Current {new_type} version\n"
            
            # Mevcut sürümleri bir satır aşağı kaydır
            updated_history = re.sub(
                r'## Version History\s*\n',
                f"## Version History\n\n{new_version_entry}",
                version_history
            )
            
            new_content = new_content.replace(version_history, updated_history)
        
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"README.md dosyasındaki sürüm bilgileri güncellendi.")
    
    # requirements.txt dosyasını güncelle
    req_path = MAIN_DIR / "requirements.txt"
    if req_path.exists():
        with open(req_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # İlk satırı güncelle
        if new_type == "release":
            header = f"# Main/requirements.txt - v{new_version}"
        else:
            header = f"# Main/requirements.txt - {new_type.capitalize()} {new_version}"
        
        new_content = re.sub(
            r'^#.*',
            header,
            content,
            count=1,
            flags=re.MULTILINE
        )
        
        with open(req_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"requirements.txt dosyasındaki sürüm bilgileri güncellendi.")
    
    # main.py dosyasını güncelle
    main_path = MAIN_DIR / "main.py"
    if main_path.exists():
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # İlk satırı güncelle
        if new_type == "release":
            header = f"# Main/main.py - v{new_version}"
        else:
            header = f"# Main/main.py - {new_type.capitalize()} {new_version}"
        
        new_content = re.sub(
            r'^#.*',
            header,
            content,
            count=1,
            flags=re.MULTILINE
        )
        
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"main.py dosyasındaki sürüm bilgileri güncellendi.")
    
    return True

def create_version_history_file():
    """
    Sürüm geçmişini takip eden bir JSON dosyası oluşturur veya günceller.
    """
    history_file = PROJECT_ROOT / "Dev" / "version_history.json"
    
    # Eğer dosya mevcutsa, içeriğini oku
    if history_file.exists():
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {"versions": []}
    else:
        history = {"versions": []}
    
    # Mevcut sürümü al
    current_version, current_type = get_current_version()
    if not current_version:
        return
    
    # Sürüm geçmişine ekle
    version_entry = {
        "version": current_version,
        "type": current_type,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "backup_path": str(OLD_DIR / f"{current_type}_{current_version.replace('.', '_').replace('-', '_')}")
    }
    
    # Eğer bu sürüm zaten eklenmediyse ekle
    if not any(v["version"] == current_version for v in history["versions"]):
        history["versions"].append(version_entry)
        
        # Dosyayı güncelle
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
        
        print(f"Sürüm geçmişi güncellendi: {current_version}")

def main():
    """
    Ana fonksiyon
    """
    print("\n" + "="*50)
    print("SpotOn Versiyon Yöneticisi")
    print("="*50)
    
    # Mevcut sürümü al
    current_version, current_type = get_current_version()
    
    if not current_version or not current_type:
        print("Hata: Mevcut sürüm bilgisi alınamadı.")
        return
    
    print(f"Mevcut sürüm: {current_version} ({current_type})")
    print("\nLütfen yapmak istediğiniz işlemi seçin:")
    print("1. Aynı sürüm tipinde ilerle (örn: alpha -> alpha)")
    print("2. Bir sonraki sürüm tipine geç (örn: alpha -> beta)")
    print("3. Tam sürüme geç (release)")
    print("4. Çıkış")
    
    choice = input("\nSeçiminiz (1-4): ")
    
    if choice == "4":
        print("Programdan çıkılıyor...")
        return
    
    if choice == "1":
        # Aynı sürüm tipinde ilerle
        print("\nHangi seviyeyi artırmak istiyorsunuz?")
        print("1. Major (X.0.0)")
        print("2. Minor (0.X.0)")
        print("3. Patch (0.0.X)")
        
        level_choice = input("\nSeçiminiz (1-3): ")
        
        if level_choice == "1":
            increment_level = "major"
        elif level_choice == "2":
            increment_level = "minor"
        elif level_choice == "3":
            increment_level = "patch"
        else:
            print("Geçersiz seçim. Programdan çıkılıyor...")
            return
        
        new_version = get_next_version(current_version, current_type, increment_level)
        new_type = current_type
    
    elif choice == "2":
        # Bir sonraki sürüm tipine geç
        if current_type == "alpha":
            new_type = "beta"
        elif current_type == "beta":
            new_type = "release"
        else:
            print("Mevcut sürüm zaten en son tip (release). Programdan çıkılıyor...")
            return
        
        new_version = get_next_version(current_version, new_type)
    
    elif choice == "3":
        # Tam sürüme geç
        new_type = "release"
        new_version = get_next_version(current_version, new_type)
    
    else:
        print("Geçersiz seçim. Programdan çıkılıyor...")
        return
    
    print(f"\nYeni sürüm: {new_version} ({new_type})")
    confirm = input("Devam etmek istiyor musunuz? (e/h): ")
    
    if confirm.lower() != "e":
        print("İşlem iptal edildi.")
        return
    
    # Mevcut sürümü yedekle
    if not backup_current_version(current_version, current_type):
        print("Yedekleme işlemi başarısız oldu. İşlem iptal ediliyor.")
        return
    
    # Sürüm geçmişini güncelle
    create_version_history_file()
    
    # Dosyalardaki sürüm numaralarını güncelle
    if update_version_in_files(new_version, new_type):
        print("\nSürüm güncelleme işlemi başarıyla tamamlandı!")
        print(f"Yeni sürüm: {new_version} ({new_type})")
    else:
        print("Sürüm güncelleme işlemi sırasında hatalar oluştu.")

if __name__ == "__main__":
    main()
