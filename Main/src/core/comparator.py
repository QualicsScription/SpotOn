# Main/src/core/comparator.py
import os
import time
import hashlib
import difflib
import logging
from datetime import datetime
from collections import Counter
import numpy as np
import pandas as pd

logging.basicConfig(
    filename='file_comparator.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SWFileParser:
    def __init__(self):
        self.feature_tree_offset = 0x1000
        self.sketch_data_offset = 0x3000
        self.geometry_offset = -0x3000

    def parse_features(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                f.seek(self.feature_tree_offset)
                feature_header = f.read(100)
                feature_data = f.read(500)

                f.seek(self.sketch_data_offset)
                sketch_data = f.read(1000)

                f.seek(self.geometry_offset, os.SEEK_END)
                geometry_data = f.read(2000)

                features = self.extract_feature_names(feature_data)
                sketches = self.extract_sketch_data(sketch_data)
                geometry_stats = self.extract_geometry_stats(geometry_data)

                return {
                    'features': features,
                    'sketches': sketches,
                    'geometry_stats': geometry_stats,
                    'raw_data': {
                        'feature_tree': feature_data,
                        'sketch_data': sketch_data,
                        'geometry': geometry_data
                    }
                }
        except Exception as e:
            logging.error(f"SolidWorks dosya parsing hatası: {e}")
            return {
                'features': [],
                'sketches': [],
                'geometry_stats': {},
                'raw_data': {
                    'feature_tree': b'',
                    'sketch_data': b'',
                    'geometry': b''
                }
            }

    def extract_feature_names(self, data):
        try:
            features = []
            i = 0
            while i < len(data):
                if data[i] > 32 and data[i] < 127:
                    start = i
                    while i < len(data) and data[i] > 32 and data[i] < 127:
                        i += 1
                    if i - start > 3:
                        feature_name = data[start:i].decode('ascii', errors='ignore')
                        features.append({
                            'name': feature_name,
                            'offset': start,
                            'params': {}
                        })
                i += 1
            return features
        except Exception as e:
            logging.error(f"Feature çıkarma hatası: {e}")
            return []

    def extract_sketch_data(self, data):
        try:
            sketches = []
            markers = [b'SKET', b'LINE', b'CIRC', b'RECT']
            for marker in markers:
                pos = 0
                while True:
                    pos = data.find(marker, pos)
                    if pos == -1:
                        break
                    sketches.append({
                        'type': marker.decode('ascii'),
                        'offset': pos,
                        'data': data[pos:pos+20]
                    })
                    pos += len(marker)
            return sketches
        except Exception as e:
            logging.error(f"Sketch çıkarma hatası: {e}")
            return []

    def extract_geometry_stats(self, data):
        try:
            stats = {
                'signature': hashlib.md5(data).digest(),
                'data_size': len(data)
            }
            volume_markers = [b'VOL', b'VOLUME']
            for marker in volume_markers:
                pos = data.find(marker)
                if pos != -1 and pos + len(marker) + 8 <= len(data):
                    try:
                        import struct
                        stats['volume'] = abs(struct.unpack('d', data[pos+len(marker):pos+len(marker)+8])[0])
                        break
                    except:
                        pass
            if 'volume' not in stats:
                stats['volume'] = 1.0
            return stats
        except Exception as e:
            logging.error(f"Geometri istatistikleri çıkarma hatası: {e}")
            return {'signature': b'', 'data_size': 0, 'volume': 1.0}

class SolidWorksAnalyzer:
    def __init__(self):
        self.parser = SWFileParser()
        self.weights = {
            'feature_tree': 0.5,
            'sketch_data': 0.3,
            'geometry': 0.2,
            'metadata': 0.1
        }

    def read_binary_chunk(self, file_path, offset, size):
        try:
            with open(file_path, 'rb') as f:
                if offset < 0:
                    f.seek(offset, os.SEEK_END)
                else:
                    f.seek(offset)
                return f.read(size)
        except Exception as e:
            logging.error(f"Binary chunk okuma hatası: {e}")
            return b''

    def compare_feature_tree(self, file1, file2):
        return difflib.SequenceMatcher(None,
            self.read_binary_chunk(file1, 0x1000, 500),
            self.read_binary_chunk(file2, 0x1000, 500)).ratio() * 100

    def compare_sw_features(self, features1, features2):
        if not features1 or not features2:
            return 0.0

        names1 = [f['name'] for f in features1]
        names2 = [f['name'] for f in features2]
        name_sim = difflib.SequenceMatcher(None, names1, names2).ratio()

        param_sim = 0.0
        if features1 and features2:
            param_sim = sum(1 for f1 in features1 for f2 in features2
                          if f1['name'] == f2['name']) / max(len(features1), len(features2))

        return (name_sim * 0.7 + param_sim * 0.3) * 100

    def compare_sketches(self, sketches1, sketches2):
        if not sketches1 or not sketches2:
            return 0.0

        types1 = [s['type'] for s in sketches1]
        types2 = [s['type'] for s in sketches2]

        count1 = Counter(types1)
        count2 = Counter(types2)

        all_types = set(count1.keys()) | set(count2.keys())

        if not all_types:
            return 0.0

        similarity = sum(min(count1.get(t, 0), count2.get(t, 0)) for t in all_types) / \
                     sum(max(count1.get(t, 0), count2.get(t, 0)) for t in all_types)

        return similarity * 100

    def compare_geometry(self, geom1, geom2):
        if not geom1 or not geom2:
            return 0.0

        size_sim = 0.0
        if 'volume' in geom1 and 'volume' in geom2 and geom1['volume'] > 0 and geom2['volume'] > 0:
            size_sim = 1.0 - abs(geom1['volume'] - geom2['volume']) / max(geom1['volume'], geom2['volume'])

        sig_sim = 0.0
        if 'signature' in geom1 and 'signature' in geom2:
            sig_sim = difflib.SequenceMatcher(None, geom1['signature'], geom2['signature']).ratio()

        return (size_sim * 0.6 + sig_sim * 0.4) * 100

    def compare(self, file1, file2):
        try:
            data1 = self.parser.parse_features(file1)
            data2 = self.parser.parse_features(file2)

            binary_similarity = self.compare_feature_tree(file1, file2)

            if binary_similarity > 99.5:
                return {
                    'score': 100.0,
                    'details': {
                        'feature_tree': 100.0,
                        'sketch_data': 100.0,
                        'geometry': 100.0
                    },
                    'size_similarity': 100.0,
                    'match': True,
                    'type': 'solidworks'
                }

            feature_similarity = self.compare_sw_features(data1['features'], data2['features'])
            sketch_similarity = self.compare_sketches(data1['sketches'], data2['sketches'])
            geometry_similarity = self.compare_geometry(data1['geometry_stats'], data2['geometry_stats'])

            raw_comparisons = {}
            for key in data1['raw_data']:
                seq = difflib.SequenceMatcher(None, data1['raw_data'][key], data2['raw_data'][key])
                raw_comparisons[key] = seq.ratio() * 100

            size1 = os.path.getsize(file1)
            size2 = os.path.getsize(file2)
            size_ratio = min(size1, size2) / max(size1, size2) if max(size1, size2) > 0 else 0
            size_similarity = size_ratio * 100

            detailed_results = {
                'feature_tree': feature_similarity,
                'sketch_data': sketch_similarity,
                'geometry': geometry_similarity
            }

            total_score = (
                feature_similarity * self.weights['feature_tree'] +
                sketch_similarity * self.weights['sketch_data'] +
                geometry_similarity * self.weights['geometry']
            ) / (self.weights['feature_tree'] + self.weights['sketch_data'] + self.weights['geometry'])

            raw_score = sum(raw_comparisons.values()) / len(raw_comparisons) if raw_comparisons else 0

            final_score = total_score * 0.8 + raw_score * 0.15 + size_similarity * 0.05

            is_match = final_score > 98

            return {
                'score': final_score,
                'details': detailed_results,
                'raw_comparisons': raw_comparisons,
                'size_similarity': size_similarity,
                'match': is_match,
                'type': 'solidworks'
            }
        except Exception as e:
            logging.error(f"SolidWorks karşılaştırma hatası: {e}")
            return {'score': 0, 'match': False, 'type': 'solidworks', 'details': {}}

class GeneralComparator:
    def __init__(self):
        pass

    def compare(self, file1, file2):
        try:
            stat1 = os.stat(file1)
            stat2 = os.stat(file2)

            size_diff = abs(stat1.st_size - stat2.st_size)
            max_size = max(stat1.st_size, stat2.st_size)
            size_similarity = (1 - (size_diff / max_size)) * 100 if max_size > 0 else 0

            time_diff = abs(stat1.st_mtime - stat2.st_mtime)
            time_similarity = max(0, 100 - (time_diff / 86400 * 100)) if time_diff < 86400 else 0

            content_similarity = 0
            try:
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    header1 = f1.read(1024)
                    header2 = f2.read(1024)
                    header_similarity = difflib.SequenceMatcher(None, header1, header2).ratio() * 100

                    f1.seek(stat1.st_size // 2)
                    f2.seek(stat2.st_size // 2)
                    mid1 = f1.read(1024)
                    mid2 = f2.read(1024)
                    mid_similarity = difflib.SequenceMatcher(None, mid1, mid2).ratio() * 100

                    content_similarity = (header_similarity * 0.6 + mid_similarity * 0.4)
            except:
                content_similarity = 0

            hash_match = False
            if size_similarity > 99:
                try:
                    hash1 = hashlib.md5(open(file1, 'rb').read()).hexdigest()
                    hash2 = hashlib.md5(open(file2, 'rb').read()).hexdigest()
                    hash_match = (hash1 == hash2)
                except:
                    pass

            total_score = (
                size_similarity * 0.3 +
                time_similarity * 0.2 +
                content_similarity * 0.5
            )

            return {
                'score': total_score,
                'size_similarity': size_similarity,
                'time_similarity': time_similarity,
                'content_similarity': content_similarity,
                'match': hash_match,
                'type': 'general'
            }
        except Exception as e:
            logging.error(f"Genel karşılaştırma hatası: {e}")
            return {'score': 0, 'match': False, 'type': 'general'}

class FileComparator:
    def __init__(self):
        self.supported_extensions = {
            'solidworks': ['.sldprt', '.sldasm', '.slddrw'],
            'cad': ['.step', '.stp', '.iges', '.igs', '.stl', '.obj', '.dxf'],
            'document': ['.docx', '.xlsx', '.pdf', '.txt'],
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'],
            'all': []
        }

        self.solidworks_comparator = SolidWorksAnalyzer()
        self.general_comparator = GeneralComparator()

        for exts in self.supported_extensions.values():
            self.supported_extensions['all'].extend(exts)

    def detect_manipulation(self, file1, file2, comparison_results):
        try:
            stat1 = os.stat(file1)
            stat2 = os.stat(file2)

            indicators = {
                'size_ratio': min(stat1.st_size, stat2.st_size) / max(stat1.st_size, stat2.st_size) if max(stat1.st_size, stat2.st_size) > 0 else 0,
                'time_diff': 1 - (abs(stat1.st_mtime - stat2.st_mtime) / 86400 if abs(stat1.st_mtime - stat2.st_mtime) < 86400 else 0),
                'content_injection': max(0, comparison_results['semantic']['score'] - comparison_results['hash']['score']) / 100,
                'rename_pattern': difflib.SequenceMatcher(None, os.path.basename(file1), os.path.basename(file2)).ratio()
            }

            weights = {
                'size_ratio': 0.2,
                'time_diff': 0.3,
                'content_injection': 0.3,
                'rename_pattern': 0.2
            }

            manipulation_score = sum(indicators[key] * weights[key] for key in indicators)

            manipulation_type = 'none'
            if manipulation_score > 0.7:
                if indicators['content_injection'] > 0.5:
                    manipulation_type = 'content_injection'
                elif indicators['time_diff'] > 0.8:
                    manipulation_type = 'quick_edit'
                elif indicators['rename_pattern'] > 0.7:
                    manipulation_type = 'rename'
                else:
                    manipulation_type = 'unknown'

            return {
                'detected': manipulation_score > 0.7,
                'score': manipulation_score * 100,
                'type': manipulation_type,
                'indicators': indicators
            }
        except Exception as e:
            logging.error(f"Manipülasyon tespit hatası: {e}")
            return {
                'detected': False,
                'score': 0,
                'type': 'none',
                'indicators': {}
            }

    def classify_result(self, score, hash_match, file_type):
        if file_type == 'solidworks':
            if hash_match: return "Tam Eşleşme"
            elif score >= 98: return "Tam Eşleşme"
            elif score >= 85: return "Save As Kopyası"
            elif score >= 70: return "Küçük Değişiklikler"
            elif score >= 40: return "Büyük Değişiklikler"
            else: return "Farklı Dosyalar"
        else:
            if hash_match: return "Tam Eşleşme"
            elif score >= 95: return "Neredeyse Aynı"
            elif score >= 80: return "Çok Benzer"
            elif score >= 60: return "Orta Benzerlik"
            elif score >= 30: return "Zayıf Benzerlik"
            else: return "Farklı Dosyalar"

    def compare_files(self, file1, file2):
        try:
            ext = os.path.splitext(file1)[1].lower()
            if ext in ['.sldprt', '.sldasm', '.slddrw']:
                sw_result = self.solidworks_comparator.compare(file1, file2)
                file_type = 'solidworks'

                metadata_score = min(sw_result.get('size_similarity', 0), 30)
                details = sw_result.get('details', {})
                result = {
                    'score': sw_result['score'] * 0.8 + metadata_score * 0.2,
                    'match': sw_result.get('match', False),
                    'size_similarity': sw_result.get('size_similarity', 0),
                    'feature_tree': details.get('feature_tree', 0),
                    'sketch_data': details.get('sketch_data', 0),
                    'geometry': details.get('geometry', 0),
                    'type': 'solidworks'
                }
            else:
                result = self.general_comparator.compare(file1, file2)
                file_type = result.get('type', 'general')

            manipulation = self.detect_manipulation(file1, file2, {
                'metadata': {'score': result.get('size_similarity', 0)},
                'hash': {'score': 100 if result.get('match', False) else 0},
                'semantic': {'score': result.get('content_similarity', 0) if file_type != 'solidworks' else result.get('geometry', 0)},
                'structure': {'score': result.get('feature_tree', 0) if file_type == 'solidworks' else 0}
            })

            category = self.classify_result(result['score'], result.get('match', False), file_type)

            comparison_result = {
                'file1': file1,
                'file2': file2,
                'total': result['score'],
                'category': category,
                'manipulation': manipulation,
                'file_type': file_type,
                'match': result.get('match', False)
            }

            if file_type == 'solidworks':
                comparison_result.update({
                    'metadata': result.get('size_similarity', 0),
                    'hash': 100 if result.get('match', False) else 0,
                    'content': result.get('geometry', 0),
                    'structure': result.get('feature_tree', 0),
                    'details': {
                        'feature_tree': result.get('feature_tree', 0),
                        'sketch_data': result.get('sketch_data', 0),
                        'geometry': result.get('geometry', 0)
                    }
                })
            else:
                comparison_result.update({
                    'metadata': (result.get('size_similarity', 0) * 0.7 + result.get('time_similarity', 0) * 0.3),
                    'hash': 100 if result.get('match', False) else 0,
                    'content': result.get('content_similarity', 0),
                    'structure': 0
                })

            return comparison_result
        except Exception as e:
            logging.error(f"Dosya karşılaştırma hatası: {e}")
            return {
                'file1': file1,
                'file2': file2,
                'metadata': 0,
                'hash': 0,
                'content': 0,
                'structure': 0,
                'total': 0,
                'category': "Hata",
                'manipulation': {'detected': False},
                'file_type': 'unknown',
                'match': False,
                'error': str(e)
            }