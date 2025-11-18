from core.plugin_base import BasePlugin
import time
from selenium.common.exceptions import NoAlertPresentException

class DOMXSSPlugin(BasePlugin):
    NAME = "DOM XSS (Hash)"
    PHASE = "phase2_dom"
    PAYLOAD_TEXT = "'DOM_V7_Hash'"
    PAYLOAD_RAW = f"<img src=x onerror=alert({PAYLOAD_TEXT})>"

    def test_page(self, driver, url):
        test_url = f"{url}#{self.PAYLOAD_RAW}"
        try:
            driver.get(test_url)
            time.sleep(0.5)
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()

            if self.PAYLOAD_TEXT in alert_text:
                self.result_manager.log_vulnerability(
                    'DOM-based XSS', 'HIGH', url,
                    f'Eksekusi JS terdeteksi dari URL Hash',
                    self.PAYLOAD_RAW
                )
        except NoAlertPresentException:
            pass # Aman
        except Exception as e:
            print(f"[DOM Plugin] Error: {e}")