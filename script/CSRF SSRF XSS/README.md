```markdown
   ██████╗   ███████╗  ██╗  ██╗
  ██╔═══     ██╔════╝  ╚██╗██╔╝
  ██║        ███████╗   ╚███╔╝ 
  ██║        ╚════██║   ██╔██╗ 
  ╚██████╔╝  ███████║  ██╔╝ ██╗
   ╚═════╝   ╚══════╝  ╚═╝  ╚═╝
```
# Web Vulnerability Platform (V7.0)

Ini adalah platform pemindaian kerentanan web modular yang dapat diperluas, dirancang untuk skalabilitas dan deteksi mendalam. Proyek ini berevolusi dari skrip sederhana menjadi framework berbasis plugin yang menggunakan arsitektur hibrida (requests + selenium) dan infrastruktur ter-container (Docker).

## Desclaimer

Alat ini dibuat hanya untuk tujuan pendidikan dan pengujian keamanan yang sah. Jangan pernah menggunakannya pada sistem yang tidak Anda miliki izin tertulis untuk mengujinya. Pengguna bertanggung jawab penuh atas tindakan mereka.

## Arsitektur V7.0 (Platform Plugin)

V7.0 dirancang untuk memisahkan Logika Inti dari Logika Keamanan:

1. Inti (`core`/, `scanner_v7.py`): Bertindak sebagai orkestrator (pengatur). Tugasnya adalah mengelola crawling, antrian, threading, dan manajer (seperti OAST dan DOM). Inti ini tidak tahu apa itu "XSS" atau "SQLi".

2. Plugin (`plugins/`): Ini adalah otot pemindai. Setiap file (`.py`) di sini adalah plugin mandiri yang berisi logika untuk menemukan satu jenis kerentanan spesifik (misalnya `plugin_sqli_time.py`).

3 Infrastruktur (`docker-compose.yml`): Memisahkan "otak" (`scanner`) dari "otot" peramban (`selenium-grid`), memungkinkan pemindaian yang boros sumber daya (DOM XSS) untuk di-scale (diperluas) tanpa membebani mesin host.

### Fitur Utama
---
**1. Arsitektur Inti (Core Architecture)**

- Modular Plugin System: Menggunakan arsitektur berbasis plugin. Menambah jenis serangan baru cukup dengan menambahkan satu file `.py` di folder `plugins/` tanpa mengubah kode inti.

- **Hybrid Engine (Fase Ganda):**

    - Fase 1 (Fast Scan): Menggunakan `requests` dan `multi-threading` untuk crawling cepat dan serangan server-side (SQLi, SSRF, RCE).

    - Fase 2 (Deep Scan): Menggunakan `Selenium Grid` untuk mengeksekusi JavaScript di browser asli secara paralel guna menemukan kerentanan client-side (DOM XSS).

- **Infrastructure-as-Code:** Sepenuhnya ter-containerisasi menggunakan **Docker** dan **Docker Compose**. Memisahkan "otak" (Python) dari "otot" (Browser Chrome Nodes).

    - Anti-Stuck & Resilience: Dilengkapi mekanisme Drain Mode dan Retry Logic. Jika Selenium Grid crash atau penuh, scanner tidak akan macet (hang), melainkan melewati tugas tersebut dan melanjutkan ke pelaporan.

**2. Fitur Operasional & Kontrol**

- **AI-Powered Scanning (V11.0):**

    - Terintegrasi dengan OpenAI API (`--openai-key`).

    - Context-Aware Attacks: AI menganalisis potongan kode HTML target untuk membuat payload spesifik yang mampu mem-bypass filter WAF, alih-alih melakukan brute-force.

- **Stealth Mode (V8.0):**

    - Opsi `--stealth` untuk menghindari deteksi WAF/IPS.

    - Fitur: Rotasi User-Agent acak, Jitter (jeda waktu acak antar request), dan penyamaran header HTTP.

- **Manual Injection (Repeater Mode):**

    - Dukungan argumen `--method` dan `--data` untuk menargetkan satu endpoint API spesifik tanpa perlu crawling.

- **Selective Scanning:**

    - Opsi `--plugin-ids` untuk menjalankan hanya plugin tertentu (misal: hanya cek SSRF dan CORS).

- Safety Limits:

    - Opsi `--max-pages` untuk mencegah looping tak terbatas pada situs besar.

**3. Arsenal Serangan (Daftar Plugin)**

Scanner ini dilengkapi dengan lebih dari 30 plugin serangan yang mencakup kategori High-Impact, Modern Web, dan Infrastructure.

- **A. Kategori Injection & RCE (Critical)**

    1. **Command Injection (RCE):** Menyuntikkan perintah OS (`curl`, `nslookup`) via OAST.

    2. **Log4Shell Hunter:** Mendeteksi kerentanan JNDI Injection yang mematikan pada server Java.

    3. **SSTI (Server-Side Template Injection):** Mendeteksi eksekusi kode pada template engine (Jinja2, Twig, dll) menggunakan polyglot matematika.

    4. **SQL Injection (Time-Based):** Mendeteksi Blind SQLi dengan mengukur delay respons server.

    5. **NoSQL Injection:** Membypass autentikasi pada database MongoDB/NoSQL menggunakan payload JSON (`$ne`).

    6. **Insecure Deserialization:** Mendeteksi objek serialisasi berbahaya pada Java, PHP, dan Python.

- **B. Kategori Modern Web & API**

    1. **LLM Prompt Injection:** Menyerang fitur AI Chatbot untuk membocorkan System Prompt.

    2. **Server-Side Prototype Pollution (SSPP):** Menyerang backend Node.js dengan mencemari objek prototype JSON.

    3. **Client-Side Prototype Pollution:** Mendeteksi pencemaran objek global window di browser (DOM).

    4. **GraphQL Introspection:** Mencoba membocorkan seluruh skema database API GraphQL.

    5. **CORS Misconfiguration:** Mendeteksi konfigurasi Cross-Origin yang mengizinkan pencurian data kredensial.

    6. **JWT None Algorithm:** Mencoba memalsukan token admin dengan menghapus tanda tangan digital.

- **C. Kategori Infrastruktur & Cloud**

    1. **Cloud Metadata Stealer:** Mencoba mencuri kredensial IAM Role dari AWS, GCP, dan Azure via SSRF.

    2. **Subdomain Takeover:** Mendeteksi subdomain yang menunjuk ke layanan cloud yang sudah ditinggalkan (S3, Heroku).

    3. **Firebase Database Takeover:** Mendeteksi database Firebase yang terbuka untuk publik (`.json`).

    4. **Spring Boot Actuator Hunter:** Mencari endpoint debug Java yang terbuka (`/heapdump`, `/env`) yang membocorkan password/key.

    5. **Sensitive File Hunter:** Mencari sisa file `.git`, `.env`, dan backup database.

- **D. Kategori Protokol & Logika**

    1. **SSRF (Blind OAST):** Mendeteksi Server-Side Request Forgery menggunakan interaksi luar jalur *(Out-of-Band)* via Interact.sh.

    2. **XXE (XML External Entity):** Menyuntikkan entitas XML jahat untuk membaca file server atau SSRF.

    3. **HTTP Request Smuggling (Timing):** Mendeteksi desinkronisasi antara frontend dan backend server.

    4. **Host Header Injection:** Mencoba meracuni cache atau link reset password via manipulasi header Host.

    5. **Race Condition Hunter:** Mengirim request paralel serentak untuk mengeksploitasi celah logika transaksi (misal: kupon ganda).

    6. **403/401 Bypass:** Mencoba menembus halaman admin dengan memanipulasi header (`X-Forwarded-For`, `X-Original-URL`).

    7. **Web Cache Deception:** Memanipulasi ekstensi URL untuk menipu CDN agar menyimpan halaman sensitif pengguna.

    8. **CRLF Injection:** Mencoba memecah respons HTTP untuk menyuntikkan cookie palsu atau XSS.

- **E. Kategori XSS & Client-Side**

    1. **Reflected XSS:** Mendeteksi pantulan input berbahaya di HTML.

    2. **AI-Driven XSS:** Menggunakan AI untuk membuat payload XSS yang lolos filter berdasarkan konteks kode.

    3. **DOM XSS:** Mendeteksi eksekusi JavaScript berbahaya di sisi klien (mendukung source dari URL Hash, LocalStorage, Window.name).

    4. **JS Secrets Scanner:** Mengekstrak API Key (AWS, Google) dan endpoint tersembunyi dari file JavaScript statis.

**4. Pelaporan (Reporting)**

- **JSON Report:** Hasil scan disimpan dalam format JSON terstruktur yang mudah diolah.

- **Kategorisasi Risiko:** Temuan dikelompokkan berdasarkan tingkat keparahan (CRITICAL, HIGH, MEDIUM, LOW, INFO).

- **Bukti (Evidence):** Menyertakan URL target, deskripsi kerentanan, dan payload yang berhasil digunakan.

### Prasyarat
---
Anda HARUS memiliki perangkat lunak berikut terinstal di mesin Anda:

1. Docker Desktop (atau Docker Engine di Linux)

2. Docker Compose (biasanya sudah termasuk dalam Docker Desktop)

**Struktur Proyek**
```
scanner-v7/
├── .gitignore               # Mengabaikan file yang tidak perlu (seperti __pycache__)
├── docker-compose.yml       # Mendefinisikan & menghubungkan scanner + Selenium Grid
├── Dockerfile               # Membuat image container untuk aplikasi scanner
├── README.md                # Dokumentasi proyek (cara build, cara run)
├── requirements.txt         # Daftar semua dependensi Python (requests, selenium, dll.)
├── scanner_v7.py            # Titik masuk utama (Entrypoint). Memuat & menjalankan semua manajer.
|
├── core/                    # [INTI] Berisi semua logika orkestrasi & manajer.
│   ├── __init__.py          # Menjadikan 'core' sebagai modul Python
│   ├── crawler.py           # (Fase 1) Logika untuk crawling & menemukan vektor serangan
│   ├── dom_manager.py       # (Fase 2) Mengelola pool worker Selenium & antrian DOM
│   ├── oast.py              # Manajer untuk berinteraksi dengan Interact.sh (SSRF, dll.)
│   ├── plugin_base.py       # [PENTING] Interface (Base Class) yang harus diikuti semua plugin
│   ├── plugin_loader.py     # Logika untuk mencari & mengimpor file dari folder 'plugins/'
│   ├── selenium_driver.py   # Berisi konfigurasi ChromeOptions agar kode lebih bersih
│   ├── stealth_session.py   # Rotasi User-Agent, Jitter, Header palsu agar terlihat seperti manusia.
│   ├── ai_engine.py         # .
│   L── result_manager.py    # Mengelola pencatatan, agregasi, & pelaporan hasil
|
├── plugins/                 # [PLUGIN] Berisi semua logika deteksi kerentanan.
│   ├── __init__.py          # Menjadikan 'plugins' sebagai modul Python
│   ├── plugin_dom_xss.py    # Plugin #1: Tes DOM XSS (Fase 2, Selenium)
│   ├── plugin_headers.py    # Plugin #2: Tes Header Keamanan (Fase 1, Requests)
│   ├── plugin_reflected_xss.py # Plugin #3: Tes Reflected XSS (Fase 1, Requests)
│   ├── plugin_sqli_time.py  # Plugin #4: Tes SQLi Time-based (Fase 1, Requests)
│   ├── plugin_cors.py       # Plugin #5: Jika server memantulkan origin dan mengizinkan kredensial, itu rentan.
│   ├── plugin_graphql.py    # Plugin #6: Meminta server membeberkan seluruh skema database-nya.
│   ├── plugin_host_header.py # Plugin #7: Memanipulasi header Host
│   ├── plugin_js_secrets.py # Plugin #8: Mencari pola API Key (AWS, Google) atau endpoint tersembunyi.
│   ├── plugin_jwt_attack.py # Plugin #9: Mengubah algoritma tanda tangan JWT menjadi None.
│   ├── plugin_nosqli.py     # Plugin #10: Mengirim payload JSON ({"$ne": null}) utk manipulasi logic query login.
│   ├── plugin_proto_pollution.py # Plugin #11: Mencoba mencemari Object.prototype lewat URL dan cek dampak.
│   ├── plugin_race_condition.py  # Plugin #12:Mengirim 10 request yang sama secara bersamaan (paralel).
│   ├── plugin_sensitive_files.py # Plugin #13: Brute-force mencari file .git, .env, atau backup .sql
│   ├── plugin_ssti.py       # Plugin #14: Mengirim operasi matematika untuk mengetahui Remote Code Execution.
│   ├── plugin_takeover.py   # Plugin #15: Mengecek pesan error spesifik (misal "NoSuchBucket")
│   ├── plugin_xxe.py        # Plugin #16: Mengirim data XML jahat yang merujuk ke server OAST.
│   ├── plugin_command_injection.py # Plugin #17: Menyuntikkan perintah shell (curl, wget, nslookup, ping).
│   ├── plugin_spring_actuator.py # Plugin #18: Melakukan Force Browsing (Brute Force) pada path standar Actuator.
│   ├── plugin_crlf.py       # Plugin #19: Menyisipkan karakter baris baru (%0d%0a atau \r\n).
│   ├── plugin_log4shell.py  # Plugin #20: Menyuntikkan payload JNDI (${jndi:ldap://oast...}) ke semua header HTTP dan parameter.
│   ├── plugin_403_bypass.py # Plugin #21: Mencari parameter URL dan menggantinya dengan endpoint metadata cloud spesifik.
│   ├── plugin_cloud_metadata.py  # Plugin #22: Mendeteksi halaman 403/401, lalu membombardir dengan header bypass dan variasi URL.
│   ├── plugin_llm_injection.py   # Plugin #23: Mengirimkan perintah "Jailbreak" ke setiap input teks (chat, search, comments)
│   ├── plugin_deserialization.py # Plugin #24: Mendeteksi format serialisasi (Base64 Java, PHP serialized string, Python Pickle).
│   ├── plugin_sspp.py       # Plugin #25: Mengirim payload JSON yang mencoba mencemari properti __proto__.
│   ├── plugin_wcd.py        # Plugin #26: Celah ini memanfaatkan cara kerja CDN (Content Delivery Network).
│   ├── plugin_firebase.py   # Plugin #27: Kebocoran data pengguna (email, chat, token) atau penghapusan database total.
│   ├── plugin_request_smuggling.py  # Plugin #28: Kita mengirim request yang sengaja dibuat ambigu.
│   ├── plugin_ai_xss.py     # Plugin #29: .
│   L── plugin_ssrf_oast.py  # Plugin #30: Tes SSRF OAST (Fase 1, Requests).
|
L── reports/                 # [OUTPUT] Laporan JSON akan disimpan di sini.
    L── .gitkeep             # File placeholder agar folder ini tetap ada di Git
```

**1. Setup (Hanya Sekali)**

Sebelum Anda dapat menjalankan pemindaian, Anda perlu mem-build image Docker lokal untuk aplikasi scanner.

Buka terminal di direktori root proyek ini (di mana `docker-compose.yml` berada).

Jalankan perintah build:

```bash
docker-compose build
```

Ini akan membaca `Dockerfile`, menginstal Python, dan menginstal semua dependensi dari `requirements.txt` ke dalam image Docker bernama `scanner`.

**2. Cara Menjalankan Pemindaian**

Anda tidak lagi menjalankan `python scanner.py`. Anda menggunakan `docker-compose` untuk memulai seluruh infrastruktur (scanner + grid).

Perintah dasarnya adalah `docker-compose run --rm scanner [ARGUMEN ANDA DI SINI]`.

`run --rm scanner`: Memerintahkan Docker Compose untuk menjalankan layanan `scanner` (didefinisikan di `docker-compose.yml`) dan menghapus container-nya setelah selesai (`--rm`).

**Contoh 1: Pemindaian Cepat (Fase 1 Saja)**

Ini akan menjalankan crawling dan semua plugin Fase 1 (Reflected XSS, SQLi, SSRF) tanpa memulai Selenium. Ini adalah cara tercepat untuk mendapatkan gambaran.

```bash
docker-compose run --rm scanner "[http://example.com](http://example.com)"
```

**Contoh 2: Pemindaian Penuh (Fase 1 & Fase 2)**

Ini akan menjalankan pemindaian Fase 1, lalu memulai pemindaian Fase 2 (`--dom-xss`) secara paralel menggunakan 4 thread (default) di Selenium Grid.

```bash
docker-compose run --rm scanner "[http://example.com](http://example.com)" --dom-xss
```


**Contoh 3: Pemindaian Penuh & Lanjutan (Target Sesungguhnya)**

Ini adalah contoh realistis:

- Target: `http://test-target.com`

- Menyertakan cookie sesi untuk area yang diautentikasi.

- Menjalankan Fase 1 dengan 15 thread.

- Menjalankan Fase 2 dengan 8 thread.

- Menyimpan laporan sebagai `test-target.json.`

```bash
docker-compose run --rm scanner "[http://test-target.com](http://test-target.com)" \
    -c '{"session_id":"abc123xyz"}' \
    -t 15 \
    --dom-xss \
    --dom-threads 8 \
    -o "test-target.json"
```

**Contoh 4: Menjalankan dengan Key**
```bash
docker-compose run --rm scanner "https://target.com" --openai-key "sk-proj-....."
```

**3. Mengakses Laporan**

Berkat volumes: `./reports:/app/reports` di `docker-compose.yml`, semua file yang disimpan oleh container di `/app/reports` akan secara otomatis muncul di folder `reports/` di komputer lokal Anda.

Setelah pemindaian selesai, periksa folder `reports/` untuk file JSON Anda (misal: `test-target.json`).

**4. (OPSIONAL) Mempercepat Pemindaian Fase 2 (Scaling)**

Pemindaian Fase 2 (`--dom-xss`) dibatasi oleh jumlah node browser yang Anda miliki. Secara default, kita hanya menjalankan 1 (`chrome-node`). Jika Anda mengatur `--dom-threads=8` tetapi hanya memiliki 1 node, 7 thread lainnya akan menunggu.

Untuk mempercepat: Anda dapat "menambah" (scale) jumlah node browser.

Mulai Selenium Grid dengan 5 Browser (Node):
(Jalankan ini di terminal terpisah dan biarkan berjalan)

```bash
docker-compose up -d --scale chrome-node=5
```

Jalankan Pemindaian Anda dengan 5 Thread:
(Jalankan di terminal asli Anda)

```bash
docker-compose run --rm scanner "[http://example.com](http://example.com)" --dom-xss --dom-threads=5
```

Sekarang, pemindaian Fase 2 Anda akan berjalan 5x lebih cepat karena 5 thread scanner Anda masing-masing memiliki browser khusus untuk bekerja.

Matikan Grid setelah selesai:

```bash
docker-compose down
```


**5. (PENTING) Cara Menambahkan Plugin Baru**

Inilah kekuatan V7.0.

Contoh: Anda ingin menambahkan pemindai LFI (Local File Inclusion).

1. Buat File Baru:
Buat file bernama `plugins/plugin_lfi.py.`

2. Tulis Logika Plugin:
Pastikan Anda inherit dari `BasePlugin` dan implementasikan metode yang diperlukan.

```bash
# plugins/plugin_lfi.py
from core.plugin_base import BasePlugin

class LFIPlugin(BasePlugin):
    NAME = "LFI (Local File Inclusion)"
    PHASE = "phase1" # Ini adalah tes berbasis requests

    LFI_PAYLOAD = "../../../../etc/passwd"

    def test_vector(self, vector, session):
        """Dipanggil untuk setiap parameter GET/POST."""
        method, url, params = vector

        for param_name in params:
            test_params = params.copy()
            test_params[param_name] = self.LFI_PAYLOAD

            try:
                if method == 'GET':
                    resp = session.get(url, params=test_params, timeout=5, ...)
                else:
                    resp = session.post(url, data=test_params, timeout=5, ...)

                # Logika deteksi Anda
                if "root:x:0:0" in resp.text:
                    self.result_manager.log_vulnerability(
                        'LFI', 'HIGH', url,
                        f"Potensi LFI di param {method}: {param_name}",
                        self.LFI_PAYLOAD
                    )
            except Exception:
                pass
```

3. Selesai.

Itu saja. Anda tidak perlu mengedit `scanner_v7.py` atau file `core/` apa pun. `plugin_loader` akan secara otomatis menemukan, mengimpor, dan menjalankan plugin baru Anda pada pemindaian berikutnya.
