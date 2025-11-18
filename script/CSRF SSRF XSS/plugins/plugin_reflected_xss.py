from core.plugin_base import BasePlugin
import html
# ... (import lain jika perlu)

class ReflectedXSSPlugin(BasePlugin):
    NAME = "Reflected XSS"
    PHASE = "phase1"
    PAYLOAD = "<script>alert('Reflected_XSS')</script>"

    def test_vector(self, vector, session):
        method, url, params = vector
        test_params = params.copy()

        for param_name in test_params:
            test_params[param_name] = self.PAYLOAD

            try:
                if method == 'GET':
                    resp = session.get(url, params=test_params, timeout=5, verify=False, allow_redirects=False)
                else: # POST
                    resp = session.post(url, data=test_params, timeout=5, verify=False, allow_redirects=False)

                if self.PAYLOAD in resp.text and html.escape(self.PAYLOAD) not in resp.text:
                    self.result_manager.log_vulnerability(
                        'Reflected XSS', 'HIGH', url,
                        f"Reflected XSS di parameter {method}: {param_name}",
                        self.PAYLOAD
                    )
            except Exception:
                pass # Gagal, lanjut