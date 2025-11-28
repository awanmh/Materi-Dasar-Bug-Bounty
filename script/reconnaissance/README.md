
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

### Fitur Utama

* **🧠 AI Neural Engine (BARU v17):** Menggunakan Google Gemini untuk menganalisis halaman web secara kontekstual dan memprediksi *path* tersembunyi (Context-Aware Scanning).
* **🕵️ Hidden Asset Hunter:**
    * **Source Maps:** Merekonstruksi kode sumber asli dari file `.js.map` yang bocor.
    * **Broken Link Hijacking:** Mendeteksi tautan eksternal mati yang rentan diambil alih.
* **☁️ Infrastructure Killer:**
    * **Cloud Enumeration:** Menemukan bucket S3, Azure Blob, dan GCP publik.
    * **Port Scanning:** Pemindaian port ringan untuk layanan non-HTTP.
    * **Subdomain Takeover:** Deteksi otomatis kerentanan CNAME.
* **🔌 API Hunter:** Parsing otomatis dokumentasi **Swagger/OpenAPI** dan serangan introspeksi **GraphQL**.
* **📸 Visual Recon:** Pengambilan *screenshot* otomatis dalam mode *headless*.
* **💎 Secret Scanning:** Pencarian otomatis API Key, Token, dan Kredensial di HTML & JS.
* **🧩 Advanced Template Engine:** Logika deteksi kustom berbasis YAML/JSON dengan dukungan *Chaining* dan *Extraction*.

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
    ├── ai_brain.py
    └── utils.py            # Helpers (Warna, ProgressBar, Loader YAML/JSON)
```

-----

### Instalasi & Setup

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
pip install aiohttp aiodns tqdm pyppeteer aiosqlite PyYAML lxml beautifulsoup4 google-generativeai
```

#### 4\. Setup Pyppeteer (Browser Headless)

Ini adalah langkah paling penting. Pyppeteer perlu mengunduh *binary* Chromium yang digunakannya.

```bash
pyppeteer-install
# (Opsional) Set API Key Gemini di environment variable
# Windows PowerShell:
$env:GEMINI_API_KEY="AIzaSy..."
```

*(Ini akan mengunduh file \~100-200MB. Jika gagal di Linux, Anda mungkin perlu menginstal dependensi tambahan: `sudo apt-get install -y libpangocairo-1.0-0 libx11-xcb1 ...`)*

#### 5\. Siapkan Wordlist

*Framework* ini tidak menyertakan *wordlist*. Anda harus menyediakannya. Unduh *wordlist* umum (seperti dari [Seclists](https://github.com/danielmiessler/SecLists)) dan letakkan di folder `wordlists/` atau di mana saja.

  * `subs.txt` (untuk subdomains, misal: `subdomains-top1mil-5000.txt`)
  * `dirs.txt` (untuk direktori, misal: `directory-list-2.3-medium.txt`)

-----

### Usage (Argumen)

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

### Skenario Penggunaan (Real Cases)

Berikut adalah cara menggunakan alat ini untuk berbagai situasi bug bounty di dunia nyata.

**1. The Neural Scan (AI-Powered Discovery) - TERBARU**

Gunakan ini untuk target yang kompleks di mana brute-force biasa gagal. AI akan membaca halaman utama dan menebak endpoint berdasarkan logika bisnis target.

```bash
python recon-v17.0.py target.com \
  -t ./templates -sw wordlists/subs.txt -dw wordlists/dirs.txt \
  -c 20 \
  --ai \
  --gemini-api "AIzaSyYourKeyHere..."
```

**2. The Hidden Asset Hunt (Mode Penuh)**

Mode ini mengaktifkan Headless Browser untuk merender JavaScript. Wajib digunakan untuk aplikasi modern (SPA) guna menemukan Source Maps, Broken Links, dan DOM Secrets.

Fitur aktif: Source Map, BLH, API Hunting, Cloud Buckets, Ports, Secrets, Screenshots, Wayback.

```bash
python recon-v17.0.py target.com `
  -t ./templates `
  -sw wordlists/subs.txt `
  -dw wordlists/dirs.txt `
  -o ./hasil_scan_full `
  -c 10 `
  --headless `
  --screenshot `
  --api `
  --cloud `
  --ports `
  --wayback
```

(Catatan: -c 10 digunakan agar browser headless tidak membebani CPU/RAM).

**3. Pemindaian Standar (Mode Cepat/HTTP)**

Jika Anda ingin hasil cepat dan tidak peduli dengan render JS atau Screenshot. Fitur Source Map dan BLH tetap berjalan tapi hanya pada HTML statis.

```bash
python recon-v17.0.py target.com \
  -t ./templates \
  -sw wordlists/subs.txt \
  -dw wordlists/dirs.txt \
  -o ./hasil_cepat \
  -c 50 \
  --api
```

**4. Pemindaian Terotentikasi (Authenticated Recon)**

Memindai area admin atau dashboard pengguna.

```bash
python recon-v17.0.py app.target.com \
  -t ./templates -sw wordlists/subs.txt -dw wordlists/dirs.txt \
  --headless \
  -b "session_id=YOUR_COOKIE_HERE" \
  --auth-check-url "https://app.target.com/api/user/me" \
  --auth-check-string "Unauthenticated"
```

**5. Melanjutkan Pemindaian (Resume)**
Jika pemindaian besar terhenti di tengah jalan, lanjutkan tanpa kehilangan data.

```bash
# Tidak perlu wordlist lagi, data dimuat dari recon.db
python recon-v17.0.py target.com -o ./hasil_scan_full --resume
```

**6. Mengatasi Masalah Pyppeteer (Custom Chrome Path)**

Jika Anda mendapatkan error Chromium downloadable not found atau koneksi lambat saat mengunduh browser.

```bash
python recon-v17.0.py target.com \
  -t ./templates -sw wordlists/subs.txt -dw wordlists/dirs.txt \
  --headless \
  --chrome-path 'C:\Program Files\Google\Chrome\Application\chrome.exe'
```

####  Arsitektur Templat (Cara Menulis Serangan)

Anda dapat menulis logika serangan kustom dalam format YAML.

Contoh: `templates/cve-check.yaml`.

```bash
id: cve-2024-xxxx-check
info:
  name: "Critical Auth Bypass Check"
  severity: "critical"
target: "host" 

requests:
  # Request 1: Coba bypass login
  - method: "POST"
    path: "{{base_url}}/api/login"
    body: '{"user":"admin","bypass":true}'
    
    # Ekstrak token jika berhasil
    extractors:
      - type: "json" 
        jsonpath: "token"
        name: "auth_token"

  # Request 2: Gunakan token untuk akses admin (Chaining)
  - method: "GET"
    path: "{{base_url}}/api/admin/users"
    headers:
      Authorization: "Bearer {{auth_token}}"
    
    # Validasi keberhasilan
    matchers_condition: "and"
    matchers:
      - type: "status"
        status: 200
      - type: "word"
        part: "body"
        words:
          - "users_list"
          - "admin_role"
```
