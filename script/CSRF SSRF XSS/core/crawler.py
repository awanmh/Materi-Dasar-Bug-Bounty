import requests
import threading
import time
import json
from queue import Queue
from urllib.parse import urljoin, urlparse, parse_qs
from bs4 import BeautifulSoup, Comment
import re
import xml.etree.ElementTree as ET

class Crawler:
    """
    (Fase 1) Bertugas melakukan crawling, menemukan vektor serangan,
    dan mengirimkan tugas ke plugin Fase 1.
    """
    def __init__(self, start_url, shared_context, phase1_plugins, num_threads):
        self.start_url = start_url
        self.domain = shared_context["domain"]
        self.result_manager = shared_context["result_manager"]
        self.phase1_plugins = phase1_plugins
        self.num_threads = num_threads
        
        self.url_queue = Queue()
        self.visited_pages = set()
        self.tested_vectors = set() # Mencegah pengujian vektor yang sama berulang kali
        self.tested_vectors_count = 0
        
        self.lock = threading.Lock()
        
        # Buat sesi requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        if shared_context.get("cookie"):
            try:
                self.session.cookies.update(json.loads(shared_context["cookie"]))
                print("[*] Crawler: Berhasil memuat cookie sesi.")
            except Exception as e:
                print(f"[-] Crawler: Gagal memuat cookie: {e}")

        # Injeksi konteks ke plugin
        for plugin in self.phase1_plugins:
            plugin.set_context(shared_context)

    def add_to_queue(self, url):
        """Helper untuk menambahkan URL ke antrian jika valid."""
        # Bersihkan parameter dan hash
        base_url = url.split('#')[0].split('?')[0]
        
        with self.lock:
            if (urlparse(base_url).netloc == self.domain and
                base_url not in self.visited_pages):
                
                self.visited_pages.add(base_url)
                self.url_queue.put(base_url)

    def run_crawl_and_scan(self):
        """Memulai thread worker crawler."""
        self.crawl_entrypoints() # Cari sitemap/robots
        self.add_to_queue(self.start_url)
        
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()
            threads.append(t)
            
        self.url_queue.join()
        
        # Kirim sinyal berhenti
        for _ in range(self.num_threads):
            self.url_queue.put(None)
        for t in threads:
            t.join()

    def worker(self):
        """Worker thread untuk crawling dan memicu pemindaian."""
        while True:
            try:
                url = self.url_queue.get()
                if url is None:
                    break # Sinyal berhenti

                try:
                    response = self.session.get(url, timeout=5, verify=False, allow_redirects=True)
                except requests.RequestException as e:
                    print(f"[-] Crawler: Gagal mengambil {url}: {e}")
                    self.url_queue.task_done()
                    continue

                # 1. Crawl halaman ini untuk link baru
                self.crawl_page(url, response)
                
                # 2. Jalankan Plugin "per-halaman" (misal: Headers)
                for plugin in self.phase1_plugins:
                    try:
                        plugin.test_page(url, response, self.session)
                    except Exception as e:
                        print(f"[!] Error di plugin {plugin.NAME} (test_page): {e}")

                # 3. Temukan & Jalankan Plugin "per-vektor" (misal: XSS, SQLi)
                vectors = self.discover_vectors(url, response)
                for vector in vectors:
                    # Cek jika vektor sudah diuji
                    vector_key = f"{vector[0]}:{vector[1]}:{frozenset(vector[2].keys())}"
                    with self.lock:
                        if vector_key in self.tested_vectors:
                            continue
                        self.tested_vectors.add(vector_key)
                        self.tested_vectors_count += 1

                    # Kirim vektor ke semua plugin
                    for plugin in self.phase1_plugins:
                        try:
                            plugin.test_vector(vector, self.session)
                        except Exception as e:
                            print(f"[!] Error di plugin {plugin.NAME} (test_vector): {e}")

                self.url_queue.task_done()
            except Exception as e:
                print(f"[!] Error serius di worker crawler: {e}")
                self.url_queue.task_done()

    def crawl_page(self, url, response):
        """Mencari link baru di halaman dan menambahkannya ke antrian."""
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return

        try:
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Cari di <a> tags
            for link in soup.find_all('a', href=True):
                self.add_to_queue(urljoin(url, link['href']))
            
            # Cari di komentar
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                found_urls = re.findall(r'(?:https?://|/)[a-zA-Z0-9_./?=-]+', str(comment))
                for found_url in found_urls:
                    self.add_to_queue(urljoin(url, found_url))

            # Cari di <script> tags
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    found_urls = re.findall(r'["\']((?:https?://|/)[a-zA-Z0-9_./?=-]+)["\']', str(script.string))
                    for found_url in found_urls:
                        self.add_to_queue(urljoin(url, found_url))
        except Exception as e:
            print(f"[-] Gagal mem-parsing HTML dari {url}: {e}")

    def discover_vectors(self, url, response):
        """Menemukan semua vektor serangan (parameter GET & form POST) di halaman."""
        vectors = []
        try:
            soup = BeautifulSoup(response.text, 'lxml')

            # 1. Vektor GET (dari <a> tags)
            for link in soup.find_all('a', href=True):
                href = link['href']
                parsed_href = urlparse(href)
                if parsed_href.query:
                    base_link_url = urljoin(url, parsed_href.path)
                    params = parse_qs(parsed_href.query)
                    # Mengubah {'id': ['1']} menjadi {'id': '1'} untuk kesederhanaan
                    simple_params = {k: v[0] for k, v in params.items()}
                    vectors.append(('GET', base_link_url, simple_params))
            
            # 2. Vektor POST (dari <form>)
            for form in soup.find_all('form'):
                action_url = urljoin(url, form.get('action', ''))
                method = form.get('method', 'get').upper()
                if method != 'POST':
                    # TODO: Tangani form GET sebagai vektor GET
                    continue
                
                params = {}
                for inp in form.find_all(['input', 'textarea', 'select']):
                    name = inp.get('name')
                    if name:
                        params[name] = inp.get('value', 'test') # Nilai default
                
                if params:
                    vectors.append(('POST', action_url, params))
        except Exception as e:
             print(f"[-] Gagal menemukan vektor di {url}: {e}")
             
        return vectors

    def crawl_entrypoints(self):
        """Membaca robots.txt dan sitemap.xml."""
        # (Implementasi V5.0...)
        pass

    def parse_sitemap(self, sitemap_url):
        """Mem-parsing sitemap."""
        # (Implementasi V5.0...)
        pass