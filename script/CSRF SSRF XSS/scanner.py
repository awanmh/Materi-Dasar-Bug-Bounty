#!/usr/bin/env python3
"""
Web Vulnerability Platform - V7.0 (Plugin Architecture)
"""

import sys
import threading
import time
import argparse
import importlib
import os
from queue import Queue
from urllib.parse import urlparse

# --- Import Modul Inti ---

from core.crawler import Crawler
from core.oast import OASTManager
from core.dom_manager import DOMXSSManager
from core.result_manager import ResultManager
from core.plugin_loader import load_plugins

# ==============================================================================
# INTI: FUNGSI MAIN
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description='Web Vulnerability Platform V7.0')
    parser.add_argument('url', help='Target URL to scan')
    parser.add_argument('-c', '--cookie', help='''Session cookie in JSON format''')
    parser.add_argument('-o', '--output', help='Output file for JSON report', default='report.json')
    
    # Argumen Fase 1 (Crawl & Scan Cepat)
    parser.add_argument('-t', '--threads', type=int, default=10, help='Jumlah thread Fase 1 (Requests)')
    
    # Argumen Fase 2 (Scan DOM)
    parser.add_argument('--dom-xss', action='store_true', help='Aktifkan DOM XSS scan')
    parser.add_argument('--dom-threads', type=int, default=4, help='Jumlah worker paralel DOM')
    parser.add_argument('--grid-url', type=str, default='http://selenium-hub:4444/wd/hub')
    
    args = parser.parse_args()
    
    if not args.url.startswith(('http://', 'https://')):
        args.url = 'http://' + args.url
    
    print("Web Vulnerability Platform (V7.0 - Plugin Architecture)")
    print("=" * 60)
    
    start_time = time.time()
    
    # 1. Inisialisasi Manajer
    print("[*] Menginisialisasi manajer inti...")
    result_manager = ResultManager()
    oast_manager = OASTManager()
    
    # Berbagi antrian dan manajer di seluruh sistem
    # Ini adalah "bus" data kita
    shared_context = {
        "result_manager": result_manager,
        "oast_manager": oast_manager,
        "cookie": args.cookie,
        "domain": urlparse(args.url).netloc
    }
    
    # 2. Muat Plugin
    # Memindai folder 'plugins' dan memuat semua modul
    print("[*] Memuat semua plugin pemindai dari folder /plugins...")
    plugins = load_plugins()
    print(f"[*] Berhasil memuat {len(plugins)} plugin: {[p.NAME for p in plugins]}")

    # 3. FASE 1: Crawling & Scan Cepat (Server-Side)
    print("\n" + "-"*50)
    print("[*] Memulai FASE 1: Crawling & Scan Cepat (Requests)...")
    
    # Antrian vektor adalah [ (metode, url, params_dict), ... ]
    vector_queue = Queue() 
    
    # Crawler sekarang hanya mencari halaman DAN vektor, lalu memasukkannya ke antrian
    crawler = Crawler(args.url, shared_context, vector_queue, plugins["phase1"], args.threads)
    crawler.run_crawl_and_scan() # Ini adalah fungsi V6 yang dimodifikasi
    
    print(f"[*] FASE 1: Selesai. Menemukan {len(crawler.visited_pages)} halaman unik.")

    # 4. FASE 2: Scan Dalam (DOM XSS)
    if args.dom_xss:
        print("\n" + "-"*50)
        dom_plugins = plugins.get("phase2_dom", [])
        if dom_plugins:
            dom_manager = DOMXSSManager(
                list(crawler.visited_pages), # Halaman yang ditemukan
                dom_plugins,                 # Plugin DOM
                shared_context,
                args.dom_threads,
                args.grid_url
            )
            dom_manager.run_phase2_scan()
        else:
            print("[*] FASE 2: --dom-xss diaktifkan tetapi tidak ada plugin Fase 2 yang dimuat.")
    else:
        print("\n[*] FASE 2: DOM XSS scan dilewati.")

    # 5. FASE 3: Pengumpulan Hasil (OAST)
    print("\n" + "-"*50)
    print("[*] Memulai FASE 3: Pengumpulan Hasil Asinkron (OAST)...")
    oast_manager.check_interactions()

    # --- LAPORAN AKHIR ---
    print("\n" + "="*60)
    print("SCAN SELESAI")
    print("=" * 60)
    end_time = time.time()
    
    result_manager.generate_report(
        scan_duration = end_time - start_time,
        pages_found = len(crawler.visited_pages),
        vectors_tested = crawler.tested_vectors_count
    )
    
    report_path = os.path.join("/app/reports", args.output)
    result_manager.save_report(report_path)

if __name__ == "__main__":
    # Kita perlu menambahkan folder 'core' dan 'plugins' ke path Python
    sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'plugins'))
    main()