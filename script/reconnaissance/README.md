
-----

```markdown
  ▄████████    ▄██████▄     ▄████████  ▄██████▄    ████████▄
  ███    ███   ███    ███   ███    ███ ███    ███  ███    ███
  ███    █▀    ███    ███   ███    █▀  ███    ███  ███    ███
  ███          ███    ███  ▄███▄▄▄     ███    ███  ███    ███
  ███        ▀███████████ ▀▀███▀▀▀   ▀███████████  ███    ███
  ███    █▄    ███    ███   ███    █▄  ███    ███  ███    ███
  ███    ███   ███    ███   ███    ███ ███    ███  ███    ███
  ████████▀    ███    █▀    ██████████ ███    █▀   ████████▀ 
            [v16.0 - Advanced Recon Engine]
```

**RECON v16.0** adalah *framework* penilaian keamanan dinamis (DAST) yang modular, *stateful*, dan berbasis templat. Didesain untuk penelitian keamanan dan *blue teaming*, *engine* ini mampu melakukan *crawling* canggih, memvalidasi sesi, mendeteksi tumpukan teknologi (*tech stack*), dan mengeksekusi logika deteksi kustom yang ditentukan oleh Anda.

---

### ⚠️ Peringatan Legal

> **HANYA UNTUK PENGGUNAAN PROFESIONAL DAN SAH**
>
> Alat ini menjalankan templat kustom yang dapat melakukan pemindaian intrusif. Anda bertanggung jawab penuh atas templat yang Anda muat dan aktivitas yang Anda lakukan.
>
> **Jangan pernah** menjalankan alat ini terhadap target yang tidak Anda miliki izin tertulis secara eksplisit. Penggunaan tanpa izin adalah ilegal dan dilarang keras. Penulis tidak bertanggung jawab atas penyalahgunaan atau kerusakan yang disebabkan oleh alat ini.

---

### 🌟 Fitur Utama

* **Mesin Templat Canggih:** Tulis logika pemindaian Anda sendiri dalam file **YAML** atau **JSON**.
* **Stateful & Resumable:** Menggunakan **SQLite** (`--resume`) untuk menyimpan dan melanjutkan pemindaian besar.
* **Crawler Cerdas:**
    * Mode **HTTP** (Cepat) & **Headless** (`--headless`) untuk aplikasi JavaScript-heavy (React/Vue/Angular).
    * Penemuan *Endpoint* & *Parameter* (`GET` & `POST`).
    * *Crawling* Rekursif (`-r`) untuk memetakan aplikasi secara dinamis.
    * **[BARU] Technology Detection:** Mendeteksi framework, backend, dan database secara otomatis.
* **Manajemen Sesi Otomatis:**
    * Login otomatis (`--login-url`, `--login-data`).
    * Validasi sesi berkelanjutan (`--auth-check-url`, `--auth-check-string`).
    * Dukungan penuh untuk pemindaian terotentikasi (`--cookie`, `--header`).
* **Template Chaining & Variables:** Ekstrak nilai (seperti token CSRF) dari satu *request* dan gunakan di *request* berikutnya.
* **Payload Dictionaries:** Muat *wordlist* (misal: `passwords.txt`) di dalam templat untuk *brute-force*.
* **Matcher & Extractor Canggih:**
    * **Matchers:** `status`, `word`, `header`, `regex`, `binary` (hex).
    * **Extractors:** `regex`, `css`, `xpath`, `json`.
* **Penemuan Cerdas:** Deteksi *Wildcard DNS*, Analisis file `.js` untuk *endpoint* API.
* **UX Modern:** *Output* berwarna, *progress bar* (`tqdm`), dan mode senyap (`--silent`).

---

### 📂 Struktur File

```text
recon-v12/
├── recon-v12.0.py           # File utama (Entrypoint)
├── tech_signatures.json    # Tanda tangan untuk deteksi teknologi
├── js_patterns.json        # Pola Regex untuk mengekstrak path dari file .js
├── waf_signatures.json       # Tanda tangan untuk deteksi WAF
├── security_signatures.json
├── takeover_signatures.json
├── api_signatures.json
├── secrets_patterns.json
│
├── wordlists/                # (Contoh wordlist payload)
│   └── common-passwords.txt
│
├── templates/                # (Folder templat Anda)
│   ├── sensitive-env.yaml    # Contoh: Cek file .env
│   ├── basic-xss.yaml        # Contoh: Cek XSS
│   ├── csrf-extractor.yaml   # Contoh: Demo Chaining & Extractor
│   └── lfi-regex.yaml        # Contoh: Demo Matcher Regex
│
└── lib/                        # (Inti dari engine)
    ├── __init__.py
    ├── core.py             # EngineContext, EvidenceCollector
    ├── auth.py             # SessionManager, Auto-Login
    ├── database.py         # SQLite Handler (aiosqlite)
    ├── discovery.py      # Subdomain, Host, & WebCrawler (HTTP/Headless)
    ├── verification.py   # TemplateEngine, WafDetector
    └── utils.py            # Helpers (Warna, ProgressBar, Loader YAML/JSON)
```

-----

### 🖥️ Instalasi & Setup

Alat ini memerlukan **Python 3.8+**.

#### 1\. Kloning Repositori

```bash
git clone https://github.com/awanmh/Materi-Dasar-Bug-Bounty.git
cd recon-v12
```

#### 2\. Setup Virtual Environment (Sangat Direkomendasikan)

**Di Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Di Windows (Command Prompt):**

```bash
python -m venv venv
.\venv\Scripts\activate.bat
```

**Di Windows (PowerShell):**

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### 3\. Instal Dependensi

Jalankan perintah ini untuk menginstal semua *library* yang diperlukan:

```bash
pip install aiohttp aiodns tqdm pyppeteer aiosqlite PyYAML lxml beautifulsoup4
```

#### 4\. Setup Pyppeteer (Browser Headless)

Ini adalah langkah paling penting. Pyppeteer perlu mengunduh *binary* Chromium yang digunakannya.

```bash
pyppeteer-install
```

*(Ini akan mengunduh file \~100-200MB. Jika gagal di Linux, Anda mungkin perlu menginstal dependensi tambahan: `sudo apt-get install -y libpangocairo-1.0-0 libx11-xcb1 ...`)*

#### 5\. Siapkan Wordlist

*Framework* ini tidak menyertakan *wordlist*. Anda harus menyediakannya. Unduh *wordlist* umum (seperti dari [Seclists](https://github.com/danielmiessler/SecLists)) dan letakkan di folder `wordlists/` atau di mana saja.

  * `subs.txt` (untuk subdomains, misal: `subdomains-top1mil-5000.txt`)
  * `dirs.txt` (untuk direktori, misal: `directory-list-2.3-medium.txt`)

-----

### ⚙️ Usage (Argumen)

Ini adalah *output* dari argumen yang tersedia.

```text
usage: recon-v12.0.py [-h] [-o OUTPUT] [-c CONCURRENCY] [--silent] [--resume] [-r] [--headless] 
                      [-t TEMPLATES] [-sw SUBDOMAIN_WORDLIST] [-dw DIRECTORY_WORDLIST]
                      [-H HEADER] [-b COOKIE] [--login-url LOGIN_URL] [--login-data LOGIN_DATA]
                      [--auth-check-url AUTH_CHECK_URL] [--auth-check-string AUTH_CHECK_STRING] 
                      [-ua USER_AGENTS] [-p PROXY] [--chrome-path CHROME_PATH]
                      domain

🔍 RECONNAISSANCE FRAMEWORK v12.3

Core Arguments:
  domain                Target domain to analyze
  -o, --output          Output directory for results
  -c, --concurrency     Number of concurrent tasks (default: 50)
  --silent              Disable most output, only show critical findings
  --resume              Resume scan from database

Crawler Arguments:
  -r, --recursive       Enable recursive crawling
  --headless            Use headless browser (Pyppeteer) for crawling
  --chrome-path         Path to local Chrome/Edge executable (Fixes download errors)

Source Arguments:
  -t, --templates       Path to templates folder (YAML/JSON)
  -sw, --subdomain-wordlist Path to subdomain wordlist file
  -dw, --directory-wordlist Path to directory/endpoint wordlist file

Authentication & Session:
  -H, --header          Add custom header (e.g., "Auth: ...")
  -b, --cookie          Add custom cookie string (e.g., "SESSION=...")
  --login-url           URL untuk POST data login
  --login-data          Data form login (e.g., "user=a&pass=b")
  --auth-check-url      URL untuk mengecek validitas sesi
  --auth-check-string   String yang MUNCUL jika sesi TIDAK VALID (logout)

Evasion & Filter:
  -ua, --user-agents    Path to file with User-Agents for rotation
  -p, --proxy           Set a single proxy (e.g., "http://127.0.0.1:8080")
  --filter-status       Filter (ignore) responses with these status codes
  --filter-size         Filter (ignore) responses with these content lengths
```

-----

### 🚀 Skenario Penggunaan (Contoh)

#### 1\. Pemindaian Standar (Cepat & Cerdas)

Menemukan subdomain, host, *endpoint* dari *wordlist*, dan menjalankan semua templat.

```bash
python recon-v12.0.py example.com -sw wordlists/subs.txt -dw wordlists/dirs.txt -t ./templates/ -o ./scan-output -c 100
```

#### 2\. Pemindaian Aplikasi JavaScript (Headless & Rekursif)

Sempurna untuk aplikasi React/Vue/Angular. Jauh lebih lambat tetapi jauh lebih teliti. Jika pyppeteer gagal mengunduh Chromium, gunakan `--chrome-path`.

```bash
python recon-v12.0.py app.example.com \
  -sw subs.txt -dw dirs.txt \
  -t ./templates/ \
  -o ./scan-output -c 10 \
  --headless -r \
  --chrome-path 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

#### 3\. Pemindaian Terotentikasi (Setelah Login)

Memindai area yang dilindungi login menggunakan cookie sesi Anda.

```bash
python recon-v12.0.py dashboard.example.com \
  -sw subs.txt -dw dirs.txt \
  -t ./templates/ \
  -b "session_id=abc123xyz789" \
  --silent
```

#### 4\. Pemindaian dengan Auto-Login

Alat ini akan login, memvalidasi sesi, dan otomatis login ulang jika sesi mati.

```bash
python recon-v12.0.py example.com -sw subs.txt -dw dirs.txt -t ./templates/ \
    --login-url "https://example.com/login" \
    --login-data "username=scanner&password=Password123" \
    --auth-check-url "https://example.com/profile" \
    --auth-check-string "Halaman Login"
```

#### 5\. Melanjutkan Pemindaian (Resume)

Jika pemindaian 10 jam Anda gagal, Anda tidak perlu mengulang. Alat ini akan memuat temuan dari recon.db di folder output dan langsung melanjutkan ke Phase 4 (Assessment).

```bash
# Perhatikan --resume. Tidak perlu -sw atau -dw lagi.
python recon-v12.0.py example.com -t ./templates/ -o ./scan-output --resume
```
-----
#### Skenario Penggunaan (Command Examples)
**Skenario A: "The Hidden Asset Hunt" (Mode Penuh v16)**
Mode ini mengaktifkan Headless Browser untuk merender JavaScript. Ini wajib jika Anda ingin fitur Source Map Discovery dan Broken Link Hijacking bekerja maksimal (karena banyak link ada di dalam JS yang dirender).

Fitur yang aktif:

✅ Source Map Reconstruction (.js.map)

✅ Broken Link Hijacking Check

✅ API Hunting (Swagger/GraphQL)

✅ Cloud Buckets & Ports

✅ Secrets Scanning

```PowerShell
python recon-v16.0.py target.com `
  -t ./templates `
  -sw wordlists/subs.txt `
  -dw wordlists/dirs.txt `
  -o ./hasil_scan_v16 `
  -c 10 `
  --headless `
  --screenshot `
  --api `
  --cloud `
  --ports `
  --wayback
```
*(Catatan: -c 10 digunakan agar browser headless tidak membebani CPU/RAM. Jika tanpa headless, Anda bisa pakai -c 50).*

**Skenario B: Scan Cepat (HTTP Mode)**
Jika Anda ingin cepat dan tidak peduli dengan render JS atau Screenshot. Fitur Source Map dan BLH tetap berjalan tapi hanya pada HTML statis.

```bash
python recon-v16.0.py target.com `
  -t ./templates `
  -sw wordlists/subs.txt `
  -dw wordlists/dirs.txt `
  -o ./hasil_cepat `
  -c 50 `
  --api
```
**Skenario C: Mengatasi Masalah Pyppeteer (Chrome Path)**
Jika Anda mendapatkan error Chromium downloadable not found, gunakan browser Chrome/Edge yang ada di laptop Anda.

```bash
python recon-v16.0.py target.com `
  -t ./templates `
  -sw wordlists/subs.txt `
  -dw wordlists/dirs.txt `
  --headless `
  --chrome-path 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

```bash
python recon-v16.0.py target.com `
  -t ./templates `
  -sw wordlists/subs.txt `
  -dw wordlists/dirs.txt `
  --headless `
  --chrome-path 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
```
-----

### 📐 Arsitektur Templat (Cara Menulis Templat)

Ini adalah inti dari engine. Templat adalah file **YAML** (atau JSON) yang mendefinisikan *request* dan *matcher*.

Contoh `templates/basic-check.yaml`:

```text
id: nama-templat-unik
info:
  name: "Deskripsi Templat"
  severity: "high"
target: "host" 

requests:
  - method: "POST"
    path: "{{base_url}}/login"
    
    # --- PAYLOADS ---
    payload: "<test-payload-{{rand}}>"
    # ATAU gunakan file:
    # payload_file: "wordlists/passwords.txt"
    
    body: "user=admin&pass={{payload}}"
    
    # --- EXTRACTORS (Variables) ---
    extractors:
      - type: "regex" 
        part: "body" 
        regex: "name=\"_token\" value=\"(.*?)\""
        name: "csrf_token" # Disimpan sebagai {{csrf_token}}

  - method: "POST"
    # Menggunakan variabel dari request sebelumnya
    path: "{{base_url}}/admin/delete?_token={{csrf_token}}"
    body: "id=1"
    
    # --- MATCHERS (Kondisi Temuan) ---
    matchers_condition: "and"
    matchers:
      - type: "status"
        status: 200
      - type: "word"
        part: "body"
        words:
          - "Success"
          - "Deleted"
        condition: "or"
```
