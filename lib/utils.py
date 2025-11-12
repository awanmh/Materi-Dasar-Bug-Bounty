# lib/utils.py
import os
import json
import logging
import asyncio
import sys
from tqdm.asyncio import tqdm_asyncio

# --- DEPENDENSI BARU v12.0 ---
try:
    import yaml
except ImportError:
    print("[!] Dependensi 'PyYAML' tidak ditemukan. Jalankan: pip install PyYAML", file=sys.stderr)
    sys.exit(1)
try:
    from lxml import etree
    from bs4 import BeautifulSoup
except ImportError:
    print("[!] Dependensi 'lxml' dan 'beautifulsoup4' tidak ditemukan.", file=sys.stderr)
    print("[!] Jalankan: pip install lxml beautifulsoup4", file=sys.stderr)
    sys.exit(1)
# --- AKHIR DEPENDENSI BARU ---


class C:
    """Kelas ANSI Color (Tidak berubah)"""
    R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    M = '\033[95m'; C = '\033[96m'; W = '\033[0m'; BR = '\033[1;91m'
    BG = '\033[1;92m'; BY = '\033[1;93m'; BM = '\033[1;95m'; BC = '\033[1;96m'

class ProgressBar:
    """Wrapper TQDM (Tidak berubah)"""
    def __init__(self, silent=False):
        self.silent = silent
        self._progress = None
        self._lock = asyncio.Lock()
    async def create(self, total, description):
        if self.silent: return
        async with self._lock:
            self._progress = tqdm_asyncio(total=total, desc=f'{C.C}{description:<15}{C.W}', unit="tasks", bar_format='{l_bar}{bar:30}{r_bar}', colour='cyan')
    async def update(self, n=1):
        if self._progress:
            async with self._lock: self._progress.update(n)
    async def close(self):
        if self._progress:
            async with self._lock: self._progress.close()
    def log(self, message):
        if self.silent: return
        if self._progress: self._progress.write(message)
        else: print(message)

def load_wordlist_from_file(path):
    """(Tidak berubah dari v10.1)"""
    if not os.path.exists(path):
        logging.warning(f"{C.R}[!] File wordlist tidak ditemukan di {path}{C.W}")
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        return list(set(lines))
    except Exception as e:
        logging.error(f"{C.R}[!] Error saat membaca wordlist {path}: {e}{C.W}")
        return []

def load_template_file(path):
    """
    --- UPDATE v12.0 ---
    Memuat file templat (JSON atau YAML).
    """
    ext = os.path.splitext(path)[1]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            if ext == '.json':
                return json.load(f)
            elif ext in ('.yaml', '.yml'):
                return yaml.safe_load(f)
            else:
                logging.warning(f"Ekstensi file templat tidak dikenal: {path}")
                return None
    except FileNotFoundError:
        print(f"{C.R}[!] FATAL: File {path} tidak ditemukan.{C.W}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{C.R}[!] FATAL: Gagal memuat {path}: {e}{C.W}", file=sys.stderr)
        sys.exit(1)

# --- FUNGSI HELPER BARU v12.0 ---
def get_text_from_bytes(raw_body):
    """Mencoba decode bytes ke string"""
    try:
        return raw_body.decode('utf-8')
    except UnicodeDecodeError:
        return raw_body.decode('latin-1', errors='ignore')

def extract_with_json(body_str, jsonpath):
    """Mengekstrak data dari JSON menggunakan path 'a.b.c'"""
    try:
        data = json.loads(body_str)
        value = data
        for key in jsonpath.split('.'):
            if isinstance(value, list):
                value = value[int(key)]
            else:
                value = value[key]
        return str(value)
    except Exception:
        return None

def extract_with_xpath(body_str, xpath_query):
    """Mengekstrak data dari HTML menggunakan XPath"""
    try:
        tree = etree.HTML(body_str)
        matches = tree.xpath(xpath_query)
        if matches:
            return matches[0] # Mengembalikan string/node pertama
    except Exception:
        return None

def extract_with_css(body_str, css_selector, attribute):
    """Mengekstrak atribut dari elemen HTML menggunakan CSS Selector"""
    try:
        soup = BeautifulSoup(body_str, 'lxml')
        element = soup.select_one(css_selector)
        if element:
            return element.get(attribute)
    except Exception:
        return None