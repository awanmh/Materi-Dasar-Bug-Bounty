from core.plugin_base import BasePlugin

class SSRFOASTPlugin(BasePlugin):
    """
    Plugin (Fase 1) untuk mendeteksi SSRF menggunakan OAST.
    Menggunakan hook 'test_vector'.
    """
    NAME = "SSRF (OAST)"
    PHASE = "phase1"

    def test_vector(self, vector, session):
        """Dipanggil oleh crawler untuk setiap vektor (GET/POST) yang ditemukan."""
        
        # Pastikan OAST Manager tersedia
        if not self.oast_manager or not self.oast_manager.domain:
            return

        method, url, params = vector
        
        for param_name in params.keys():
            # 1. Buat payload OAST unik
            # Format info: "TIPE:METHOD:URL:PARAM"
            vector_info = f"SSRF:{method}:{url}:{param_name}"
            payload_url = self.oast_manager.get_payload(vector_info)
            
            if not payload_url:
                continue # Gagal membuat payload

            # 2. Siapkan data tes
            test_params = params.copy()
            test_params[param_name] = payload_url

            # 3. Kirim payload (Fire and Forget)
            try:
                if method == 'GET':
                    session.get(url, params=test_params, timeout=5, verify=False, allow_redirects=False)
                else: # POST
                    session.post(url, data=test_params, timeout=5, verify=False, allow_redirects=False)
            except requests.exceptions.RequestException:
                # Kita tidak peduli jika gagal, OAST bersifat 'blind'
                pass