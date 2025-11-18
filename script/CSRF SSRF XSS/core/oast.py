import threading
import uuid
from interactsh.Client import InteractShClient

class OASTManager:
    """
    Mengelola interaksi Out-of-Band (OAST) menggunakan Interact.sh.
    Menyediakan payload unik dan memeriksa interaksi di akhir.
    """
    def __init__(self):
        self.lock = threading.Lock()
        self.oast_payloads = {} # Melacak {oast_id: vector_info}
        self.interactsh = None
        self.domain = None
        
        try:
            print("[*] Menginisialisasi OAST Manager (Interact.sh)...")
            self.interactsh = InteractShClient()
            self.domain = self.interactsh.get_domain()
            print(f"[*] OAST Domain: {self.domain}")
        except Exception as e:
            print(f"[-] GAGAL memulai Interact.sh client: {e}")
            print("[-] Pemindaian OAST (SSRF) tidak akan berfungsi.")

    def get_payload(self, vector_info):
        """
        Menghasilkan payload OAST unik dan menyimpannya untuk korelasi nanti.
        vector_info (str): "TIPE:METHOD:URL:PARAM"
        """
        if not self.domain:
            return None # OAST tidak aktif

        oast_id = str(uuid.uuid4())
        payload = f"{oast_id}.{self.domain}"
        
        with self.lock:
            self.oast_payloads[oast_id] = vector_info
            
        return f"http://{payload}" # Mengembalikan URL lengkap

    def check_interactions(self, result_manager):
        """
        Memeriksa interaksi OAST di akhir pemindaian.
        """
        if not self.interactsh:
            print("[*] OAST dinonaktifkan, pemeriksaan interaksi dilewati.")
            return
        
        print("\n[*] Memeriksa interaksi OAST...")
        try:
            interactions = self.interactsh.get_interactions()
            if not interactions:
                print("[*] Tidak ada interaksi OAST yang diterima.")
                return

            print(f"[!] Diterima {len(interactions)} interaksi OAST!")
            
            for interaction in interactions:
                # Ambil ID unik dari subdomain
                oast_id = interaction['subdomain'].split('.')[0]
                
                with self.lock:
                    # Cek apakah ID ini milik kita
                    if oast_id in self.oast_payloads:
                        vector_info = self.oast_payloads[oast_id]
                        (vuln_type, method, url, param) = vector_info.split(':', 3)
                        
                        result_manager.log_vulnerability(
                            vuln_type, 'CRITICAL', url,
                            f"{vuln_type} terkonfirmasi via OAST di param {method}: {param}",
                            f"Interaksi {interaction['protocol']} dari {interaction['remote_address']}"
                        )
                        
                        # Hapus agar tidak dilaporkan ganda
                        del self.oast_payloads[oast_id]
                        
        except Exception as e:
            print(f"[-] Error saat mengambil interaksi OAST: {e}")