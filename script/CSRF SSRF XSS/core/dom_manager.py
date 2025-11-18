import threading
from queue import Queue
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

class DOMXSSManager:
    """
    (Fase 2) Mengelola pool thread untuk worker Selenium
    dan mengirimkan tugas ke plugin DOM.
    """
    def __init__(self, urls_to_test, dom_plugins, shared_context, num_dom_threads, grid_url):
        self.urls_to_test = urls_to_test
        self.dom_plugins = dom_plugins
        self.shared_context = shared_context
        self.num_dom_threads = num_dom_threads
        self.grid_url = grid_url
        self.dom_url_queue = Queue()
        
        # Injeksi konteks ke plugin DOM
        for plugin in self.dom_plugins:
            plugin.set_context(shared_context)

    def run_phase2_scan(self):
        """Memulai worker DOM XSS."""
        print(f"[*] FASE 2: Memulai DOM Scan (Parallel)...")
        print(f"[*] FASE 2: Target Grid: {self.grid_url}")
        print(f"[*] FASE 2: Meluncurkan {self.num_dom_threads} browser worker...")
        
        if not self.urls_to_test:
            print("[-] FASE 2: Tidak ada URL. Dilewati.")
            return

        for url in self.urls_to_test:
            self.dom_url_queue.put(url)

        threads = []
        for i in range(self.num_dom_threads):
            worker = DOMWorker(f"DOM-Worker-{i+1}", self.dom_url_queue, self)
            worker.daemon = True
            worker.start()
            threads.append(worker)
            
        self.dom_url_queue.join()
        
        # Kirim sinyal berhenti
        for _ in range(self.num_dom_threads):
            self.dom_url_queue.put(None)
        for t in threads:
            t.join()

        print("[*] FASE 2: Semua worker DOM telah selesai.")

class DOMWorker(threading.Thread):
    """
    Worker Selenium individu. Terhubung ke Grid, mengambil URL,
    dan menjalankannya di semua plugin DOM.
    """
    def __init__(self, name, queue, manager):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.manager = manager
        self.driver = None

    def setup_driver(self):
        """Terhubung ke Selenium Grid."""
        try:
            options = Options()
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--headless')
            options.add_argument('--log-level=3')
            options.add_argument('--disable-dev-shm-usage')
            options.set_capability("unexpectedAlertBehaviour", "accept") 
            
            self.driver = webdriver.Remote(
                command_executor=self.manager.grid_url,
                options=options
            )
            self.driver.set_page_load_timeout(10)
            return True
        except Exception as e:
            print(f"[-] {self.name}: Gagal terhubung ke Selenium Grid di {self.manager.grid_url}.")
            print(f"    Error: {e}")
            return False

    def run(self):
        """Proses utama worker."""
        if not self.setup_driver():
            return # Gagal setup, thread mati

        print(f"[*] {self.name}: Berjalan, terhubung ke Grid...")
        
        while True:
            try:
                url = self.queue.get()
                if url is None:
                    break # Sinyal berhenti
                
                print(f"[*] {self.name}: Tes DOM di {url}")
                
                # Jalankan URL ini di semua plugin DOM
                for plugin in self.manager.dom_plugins:
                    try:
                        # Plugin bertanggung jawab untuk navigasi (driver.get)
                        plugin.test_page(self.driver, url)
                    except Exception as e:
                        print(f"[!] Error di plugin {plugin.NAME} (test_page): {e}")

                self.queue.task_done()

            except WebDriverException as e:
                # Sesi browser mungkin mati
                print(f"[-] {self.name}: Browser mati atau sesi Grid berakhir. Memulai ulang driver... Error: {e}")
                if self.driver:
                    self.driver.quit()
                if not self.setup_driver():
                    print(f"[-] {self.name}: Gagal memulai ulang driver. Thread berhenti.")
                    break # Keluar dari loop jika tidak bisa restart
            except Exception as e:
                print(f"[-] {self.name}: Error tak terduga di {url}: {e}")
                self.queue.task_done()

        print(f"[*] {self.name}: Berhenti. Menutup sesi Grid...")
        if self.driver:
            self.driver.quit()