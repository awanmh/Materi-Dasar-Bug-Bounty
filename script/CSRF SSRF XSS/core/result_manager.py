import json
import threading
import os

class ResultManager:
    """
    Mengelola semua temuan kerentanan secara thread-safe dan
    menangani pembuatan laporan akhir.
    """
    def __init__(self):
        self.vulnerabilities = []
        self.lock = threading.Lock()

    def log_vulnerability(self, vuln_type, severity, url, description, payload=None):
        """
        Mencatat temuan kerentanan baru secara thread-safe.
        Mencegah duplikat.
        """
        vuln_data = {
            'type': vuln_type,
            'severity': severity,
            'url': url,
            'description': description
        }
        if payload:
            vuln_data['payload'] = payload

        # Kunci untuk mencegah race condition saat menambahkan ke list
        with self.lock:
            # Hindari duplikat
            if vuln_data not in self.vulnerabilities:
                print(f"[!] {vuln_type} Ditemukan: {description} di {url}")
                self.vulnerabilities.append(vuln_data)

    def generate_report(self, scan_duration, pages_found, vectors_tested):
        """
        Mencetak ringkasan laporan ke konsol.
        """
        print("\n" + "="*60)
        print("VULNERABILITY SCAN REPORT (V7.0)")
        print("="*60)
        print(f"Scan Duration: {scan_duration:.2f} seconds")
        print(f"Total Pages Scanned: {pages_found}")
        print(f"Total Vectors Tested: {vectors_tested}")
        print(f"Total Vulnerabilities Found: {len(self.vulnerabilities)}")
        print("="*60)
        
        if not self.vulnerabilities:
            print("[+] No vulnerabilities found!")
            return
            
        # Mengelompokkan berdasarkan jenis untuk laporan yang rapi
        vulnerabilities_by_type = {}
        for vuln in self.vulnerabilities:
            vuln_type = vuln['type']
            if vuln_type not in vulnerabilities_by_type:
                vulnerabilities_by_type[vuln_type] = []
            vulnerabilities_by_type[vuln_type].append(vuln)
        
        # Mencetak berdasarkan jenis
        for vuln_type, vulns in vulnerabilities_by_type.items():
            print(f"\n[{vuln_type}] Vulnerabilities: {len(vulns)}")
            print("-" * 40)
            
            for i, vuln in enumerate(vulns, 1):
                print(f" {i}. Severity: {vuln['severity']}")
                print(f"    URL: {vuln['url']}")
                print(f"    Description: {vuln['description']}")
                if 'payload' in vuln:
                    print(f"    Payload: {vuln['payload'][:70]}...")
                print()

    def save_report(self, filepath):
        """
        Menyimpan hasil pemindaian lengkap ke file JSON.
        """
        report_data = {
            'scan_info': {
                'scan_timestamp': time.time(),
                'total_vulnerabilities': len(self.vulnerabilities)
            },
            'vulnerabilities': self.vulnerabilities
        }
        
        try:
            # Memastikan direktori reports ada
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            print(f"[+] Laporan berhasil disimpan ke: {filepath}")
        except Exception as e:
            print(f"[-] Gagal menyimpan laporan: {e}")