# Main/src/core/utils.py
import os
import hashlib
import math
import logging
import difflib
from datetime import datetime

def get_file_info(path):
    try:
        stat = os.stat(path)
        return (
            f"📄 {os.path.basename(path)}\n"
            f"📏 Boyut: {format_size(stat.st_size)}\n"
            f"🕒 Değiştirilme: {datetime.fromtimestamp(stat.st_mtime)}\n"
        )
    except Exception as e:
        return f"Hata: {str(e)}"

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"

def compare_files(file1, file2, data1, data2):
    """
    İki dosyayı karşılaştırır ve benzerlik skorlarını döndürür.

    Args:
        file1: Birinci dosyanın yolu
        file2: İkinci dosyanın yolu
        data1: Birinci dosyanın yapısal verileri
        data2: İkinci dosyanın yapısal verileri

    Returns:
        Benzerlik skorlarını içeren bir sözlük
    """
    # Metadata karşılaştırması
    stat1 = os.stat(file1)
    stat2 = os.stat(file2)
    size_similarity = min(stat1.st_size, stat2.st_size) / max(stat1.st_size, stat2.st_size) if max(stat1.st_size, stat2.st_size) > 0 else 0
    time_diff = abs(stat1.st_mtime - stat2.st_mtime)
    time_similarity = 1 - (time_diff / (30 * 86400)) if time_diff < 30 * 86400 else 0
    metadata_score = (size_similarity + time_similarity) / 2 * 100

    # Hash karşılaştırması
    try:
        hash1 = hashlib.md5(open(file1, 'rb').read()).hexdigest()
        hash2 = hashlib.md5(open(file2, 'rb').read()).hexdigest()
        hash_score = 100 if hash1 == hash2 else 0
    except Exception as e:
        logging.error(f"Hash hesaplama hatası: {e}")
        hash_score = 0

    # İçerik karşılaştırması
    content_similarity = compare_binary_content(file1, file2)

    # Yapı karşılaştırması
    structure_score = compare_structure(data1, data2)

    return {
        'metadata': metadata_score,
        'hash': hash_score,
        'content': content_similarity,
        'structure': structure_score
    }

def compare_binary_content(file1, file2, block_size=1024):
    """
    İki dosyanın ikili içeriğini karşılaştırır.

    Args:
        file1: Birinci dosyanın yolu
        file2: İkinci dosyanın yolu
        block_size: Karşılaştırma için okunacak blok boyutu

    Returns:
        Benzerlik yüzdesi (0-100)
    """
    try:
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            total_similarity = 0
            block_count = 0
            while True:
                block1 = f1.read(block_size)
                block2 = f2.read(block_size)
                if not block1 or not block2:
                    break
                seq = difflib.SequenceMatcher(None, block1, block2)
                total_similarity += seq.ratio()
                block_count += 1
            return (total_similarity / block_count) * 100 if block_count > 0 else 0
    except Exception as e:
        logging.error(f"İkili içerik karşılaştırma hatası: {e}")
        return 0

def compare_structure(data1, data2):
    """
    İki dosyanın yapısal verilerini karşılaştırır.

    Args:
        data1: Birinci dosyanın yapısal verileri
        data2: İkinci dosyanın yapısal verileri

    Returns:
        Benzerlik yüzdesi (0-100)
    """
    try:
        tree_similarity = len(set(data1.get('features', [])) & set(data2.get('features', []))) / max(len(data1.get('features', [])), len(data2.get('features', []))) * 100 if data1.get('features') and data2.get('features') else 0
        sketch_similarity = len(set(data1.get('sketches', [])) & set(data2.get('sketches', []))) / max(len(data1.get('sketches', [])), len(data2.get('sketches', []))) * 100 if data1.get('sketches') and data2.get('sketches') else 0

        geometry_similarity = 0
        if 'geometry_stats' in data1 and 'geometry_stats' in data2:
            if 'volume' in data1['geometry_stats'] and 'volume' in data2['geometry_stats']:
                vol1 = data1['geometry_stats']['volume']
                vol2 = data2['geometry_stats']['volume']
                if vol1 > 0 and vol2 > 0:
                    geometry_similarity = 100 - (abs(vol1 - vol2) / max(vol1, vol2) * 100)

        return (tree_similarity * 0.4 + sketch_similarity * 0.3 + geometry_similarity * 0.3)
    except Exception as e:
        logging.error(f"Yapı karşılaştırma hatası: {e}")
        return 0

def calculate_file_signature(file_path):
    """
    Dosyanın imzasını hesaplar (ilk 1024 byte'ın MD5 özeti).

    Args:
        file_path: Dosya yolu

    Returns:
        MD5 özeti (hexadecimal string)
    """
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read(1024)).hexdigest()
    except Exception as e:
        logging.error(f"Dosya imzası hesaplama hatası: {e}")
        return ""

def calculate_entropy(file_path):
    """
    Dosyanın entropisini hesaplar.

    Args:
        file_path: Dosya yolu

    Returns:
        Entropi değeri (0-8)
    """
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            if not data:
                return 0
            entropy = 0
            for x in range(256):
                p_x = data.count(x) / len(data)
                if p_x > 0:
                    entropy += -p_x * math.log2(p_x)
            return entropy
    except Exception as e:
        logging.error(f"Entropi hesaplama hatası: {e}")
        return 0

def compare_signatures(file1, file2):
    """
    İki dosyanın imzalarını karşılaştırır.

    Args:
        file1: Birinci dosyanın yolu
        file2: İkinci dosyanın yolu

    Returns:
        Benzerlik yüzdesi (0 veya 100)
    """
    try:
        sig1 = calculate_file_signature(file1)
        sig2 = calculate_file_signature(file2)
        return 100 if sig1 == sig2 else 0
    except Exception as e:
        logging.error(f"İmza karşılaştırma hatası: {e}")
        return 0

def compare_entropy(file1, file2):
    """
    İki dosyanın entropi değerlerini karşılaştırır.

    Args:
        file1: Birinci dosyanın yolu
        file2: İkinci dosyanın yolu

    Returns:
        Benzerlik yüzdesi (0-100)
    """
    try:
        ent1 = calculate_entropy(file1)
        ent2 = calculate_entropy(file2)
        return 100 - abs(ent1 - ent2) / max(ent1, ent2) * 100 if max(ent1, ent2) > 0 else 0
    except Exception as e:
        logging.error(f"Entropi karşılaştırma hatası: {e}")
        return 0