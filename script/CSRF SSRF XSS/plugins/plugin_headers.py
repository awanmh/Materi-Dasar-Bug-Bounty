from core.plugin_base import BasePlugin

class SecurityHeadersPlugin(BasePlugin):
    """
    Plugin (Fase 1) untuk memeriksa ketiadaan header keamanan dasar.
    Menggunakan hook 'test_page'.
    """
    NAME = "Missing Security Headers"
    PHASE = "phase1"
    
    # Header yang DIHARAPKAN ada (dan tingkat keparahannya jika hilang)
    EXPECTED_HEADERS = {
        'Content-Security-Policy': 'MEDIUM',
        'X-Content-Type-Options': 'LOW',
        'X-Frame-Options': 'MEDIUM',
        'Strict-Transport-Security': 'LOW', # Low karena mungkin situs non-HTTPS
        'Referrer-Policy': 'LOW',
        'Permissions-Policy': 'LOW'
    }
    
    # Set untuk melacak header yang hilang per domain (agar tidak spam)
    reported_missing = set()

    def test_page(self, url, response, session):
        """Dipanggil oleh crawler untuk setiap halaman yang di-crawl."""
        
        # Konversi semua header respons menjadi huruf kecil
        response_headers_lower = {h.lower(): v for h, v in response.headers.items()}
        
        for header, severity in self.EXPECTED_HEADERS.items():
            if header.lower() not in response_headers_lower:
                
                # Kunci unik untuk header yang hilang ini
                report_key = f"{header}:{self.domain}"
                
                # Hanya laporkan sekali per domain
                if report_key not in self.reported_missing:
                    self.result_manager.log_vulnerability(
                        'Insecure Configuration', 
                        severity,
                        url,
                        f"Missing security header: {header}",
                        None
                    )
                    self.reported_missing.add(report_key)