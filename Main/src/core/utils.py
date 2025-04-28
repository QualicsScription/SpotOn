# Main/src/core/utils.py
import os
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