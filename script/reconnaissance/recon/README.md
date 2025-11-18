▄████████    ▄██████▄     ▄████████  ▄██████▄   ███    █▄███    ███   ███    ███   ███    ███ ███    ███  ███    ██████    █▀    ███    ███   ███    █▀  ███    ███  ███    ██████          ███    ███  ▄███▄▄▄     ███    ███  ███    ██████        ▀███████████ ▀▀███▀▀▀   ▀███████████  ███    ██████    █▄    ███    ███   ███    █▄  ███    ███  ███    ██████    ███   ███    ███   ███    ███ ███    ███  ███    ███████████▀    ███    █▀    ██████████ ███    █▀   ████████▀[v12.0 - Advanced Template Engine]RECON v12.0 adalah framework penilaian keamanan dinamis (DAST) yang modular, stateful, dan berbasis templat. Didesain untuk penelitian keamanan dan blue teaming, engine ini mampu melakukan crawling canggih, memvalidasi sesi, dan mengeksekusi logika deteksi kustom yang ditentukan oleh Anda.⚠️ Peringatan LegalHANYA UNTUK PENGGUNAAN PROFESIONAL DAN SAHAlat ini menjalankan templat kustom yang dapat melakukan pemindaian intrusif. Anda bertanggung jawab penuh atas templat yang Anda muat dan aktivitas yang Anda lakukan.Jangan pernah menjalankan alat ini terhadap target yang tidak Anda miliki izin tertulis secara eksplisit. Penggunaan tanpa izin adalah ilegal dan dilarang keras. Penulis tidak bertanggung jawab atas penyalahgunaan atau kerusakan yang disebabkan oleh alat ini.🌟 Fitur UtamaMesin Templat Canggih: Tulis logika pemindaian Anda sendiri dalam file YAML atau JSON.Stateful & Resumable: Menggunakan SQLite (--resume) untuk menyimpan dan melanjutkan pemindaian besar.Crawler Cerdas:Mode HTTP (Cepat) & Headless (--headless) untuk aplikasi JavaScript-heavy (React/Vue/Angular).Penemuan Endpoint & Parameter (GET & POST).Crawling Rekursif (-r) untuk memetakan aplikasi secara dinamis.Manajemen Sesi Otomatis:Login otomatis (--login-url, --login-data).Validasi sesi berkelanjutan (--auth-check-url, --auth-check-string).Dukungan penuh untuk pemindaian terotentikasi (--cookie, --header).Template Chaining & Variables: Ekstrak nilai (seperti token CSRF) dari satu request dan gunakan di request berikutnya.Payload Dictionaries: Muat wordlist (misal: passwords.txt) di dalam templat untuk brute-force.Matcher & Extractor Canggih:Matchers: status, word, header, regex, binary (hex).Extractors: regex, css, xpath, json.Penemuan Cerdas: Deteksi Wildcard DNS, Analisis file .js untuk endpoint API.UX Modern: Output berwarna, progress bar (tqdm), dan mode senyap (--silent).📂 Struktur Filerecon-v12/
├── recon-v12.0.py           # File utama (Entrypoint)
├── tech_signatures.json    # Tanda tangan untuk deteksi teknologi
├── js_patterns.json        # Pola Regex untuk mengekstrak path dari file .js
├── waf_signatures.json       # Tanda tangan untuk deteksi WAF
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
🖥️ Instalasi & SetupAlat ini memerlukan Python 3.8+.1. Kloning Repositorigit clone <url-repositori-anda>
cd recon-v12
2. Setup Virtual Environment (Sangat Direkomendasikan)Di Linux / macOS:python3 -m venv venv
source venv/bin/activate
Di Windows (Command Prompt):python -m venv venv
.\venv\Scripts\activate.bat
Di Windows (PowerShell):python -m venv venv
.\venv\Scripts\Activate.ps1
3. Instal DependensiJalankan perintah ini untuk menginstal semua library yang diperlukan:pip install aiohttp aiodns tqdm pyppeteer aiosqlite PyYAML lxml beautifulsoup4
4. Setup Pyppeteer (Browser Headless)Ini adalah langkah paling penting. Pyppeteer perlu mengunduh binary Chromium yang digunakannya.pyppeteer-install
(Ini akan mengunduh file ~100-200MB. Jika gagal di Linux, Anda mungkin perlu menginstal dependensi tambahan: sudo apt-get install -y libpangocairo-1.0-0 libx11-xcb1 ...)5. Siapkan WordlistFramework ini tidak menyertakan wordlist. Anda harus menyediakannya. Unduh wordlist umum (seperti dari Seclists) dan letakkan di folder wordlists/ atau di mana saja.subs.txt (untuk subdomains, misal: subdomains-top1mil-5000.txt)dirs.txt (untuk direktori, misal: directory-list-2.3-medium.txt)⚙️ UsageIni adalah output dari argumen yang tersedia.usage: recon-v12.0.py [-h] [-o OUTPUT] [-c CONCURRENCY] [--silent] [--resume] [-r] [--headless] -t TEMPLATES -sw SUBDOMAIN_WORDLIST -dw DIRECTORY_WORDLIST
                      [-ts TECH_SIGNATURES] [-js JS_PATTERNS] [-ws WAF_SIGNATURES] [-H HEADER] [-b COOKIE] [--login-url LOGIN_URL] [--login-data LOGIN_DATA]
                      [--auth-check-url AUTH_CHECK_URL] [--auth-check-string AUTH_CHECK_STRING] [-ua USER_AGENTS] [-p PROXY] [--filter-status FILTER_STATUS [FILTER_STATUS ...]]
                      [--filter-size FILTER_SIZE [FILTER_SIZE ...]]
                      domain

🔍 RECONNAISSANCE FRAMEWORK v12.0

Core Arguments:
  domain                Target domain to analyze
  -o, --output OUTPUT   Output directory for results
  -c, --concurrency CONCURRENCY
                        Number of concurrent tasks (default: 50)
  --silent              Disable most output, only show critical findings
  --resume              Resume scan from database

Crawler Arguments:
  -r, --recursive       Enable recursive crawling
  --headless            Use headless browser (Pyppeteer) for crawling

Source Arguments:
  -t, --templates TEMPLATES
                        Path to templates folder (YAML/JSON)
  -sw, --subdomain-wordlist SUBDOMAIN_WORDLIST
                        Path to subdomain wordlist file
  -dw, --directory-wordlist DIRECTORY_WORDLIST
                        Path to directory/endpoint wordlist file
  -ts, --tech-signatures TECH_SIGNATURES
                        Path to technology signatures JSON file
  -js, --js-patterns JS_PATTERNS
                        Path to JS regex patterns JSON file
  -ws, --waf-signatures WAF_SIGNATURES
                        Path to WAF signatures JSON file

Authentication & Session Arguments:
  -H, --header HEADER   Add custom header (e.g., "Auth: ...")
  -b, --cookie COOKIE   Add custom cookie string (e.g., "SESSION=...")
  --login-url LOGIN_URL
                        URL untuk POST data login
  --login-data LOGIN_DATA
                        Data form login (e.g., "user=a&pass=b")
  --auth-check-url AUTH_CHECK_URL
                        URL untuk mengecek validitas sesi
  --auth-check-string AUTH_CHECK_STRING
                        String yang MUNCUL jika sesi TIDAK VALID (logout)

Evasion & Filter Arguments:
  -ua, --user-agents USER_AGENTS
                        Path to file with User-Agents (one per line) for rotation
  -p, --proxy PROXY     Set a single proxy (e.g., "[http://127.0.0.1:8080](http://127.0.0.1:8080)")
  --filter-status FILTER_STATUS [FILTER_STATUS ...]
                        Filter (ignore) responses with these status codes
  --filter-size FILTER_SIZE [FILTER_SIZE ...]
                        Filter (ignore) responses with these content lengths

Example: python recon-v12.0.py example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 50
🚀 Skenario Penggunaan (Contoh)1. Pemindaian Standar (Cepat & Cerdas)Menemukan subdomain, host, endpoint dari wordlist, dan menjalankan semua templat.python recon-v12.0.py example.com -sw wordlists/subs.txt -dw wordlists/dirs.txt -t ./templates/ -o ./scan-output -c 100
2. Pemindaian Aplikasi JavaScript (Headless & Rekursif)Sempurna untuk aplikasi React/Vue/Angular. Jauh lebih lambat tetapi jauh lebih teliti.python recon-v12.0.py app.example.com -sw subs.txt -dw dirs.txt -t ./templates/ -o ./scan-output -c 10 --headless -r
3. Pemindaian Terotentikasi (Setelah Login)Memindai area yang dilindungi login menggunakan cookie sesi Anda.# -b untuk cookie, --silent untuk menyembunyikan noise
python recon-v12.0.py dashboard.example.com -sw subs.txt -dw dirs.txt -t ./templates/ -b "session_id=abc123xyz789" --silent
4. Pemindaian dengan Auto-LoginAlat ini akan login, memvalidasi sesi, dan otomatis login ulang jika sesi mati.python recon-v12.0.py example.com -sw subs.txt -dw dirs.txt -t ./templates/ \
    --login-url "[https://example.com/login](https://example.com/login)" \
    --login-data "username=scanner&password=Password123" \
    --auth-check-url "[https://example.com/profile](https://example.com/profile)" \
    --auth-check-string "Halaman Login"
5. Melanjutkan Pemindaian (Resume)Jika pemindaian 10 jam Anda gagal, Anda tidak perlu mengulang. Alat ini akan memuat temuan dari recon.db di folder output dan langsung melanjutkan ke Phase 4 (Assessment).# Perhatikan --resume. Tidak perlu -sw atau -dw lagi.
python recon-v12.0.py example.com -t ./templates/ -o ./scan-output --resume
📐 Arsitektur Templat (Cara Menulis Templat)Ini adalah inti dari engine. Templat adalah file YAML (atau JSON) yang mendefinisikan request dan matcher.Struktur Templat (YAML)# ID unik untuk templat
id: nama-templat-unik
info:
  name: "Nama templat yang mudah dibaca"
  severity: "info" # info, medium, high, critical

# Target (di mana templat ini akan dijalankan)
# - "host": Dijalankan 1x per host (misal: {{base_url}} dari live_hosts)
# - "params_get": Dijalankan untuk SETIAP parameter GET yang ditemukan
target: "host" 

# Daftar request yang akan dieksekusi SECARA BERURUTAN (Chaining)
requests:
  - method: "POST"
    path: "{{base_url}}/login"
    
    # --- PAYLOADS ---
    # 1. Payload tunggal
    payload: "<gemini-test-{{rand}}>"
    
    # 2. ATAU File Payload (untuk brute-force)
    payload_file: "wordlists/passwords.txt"
    
    # {{payload}} akan diganti di 'body' atau 'path'
    body: "user=admin&pass={{payload}}"
    
    # --- EXTRACTORS (Variables) ---
    # Dijalankan setelah request, untuk menyimpan variabel
    extractors:
      - type: "regex" # Tipe: regex, css, xpath, json
        part: "body" # Target: body, header
        regex: "name=\"_token\" value=\"(.*?)\"" # Grup (.*?) akan diekstrak
        name: "csrf_token" # Disimpan sebagai {{csrf_token}}

  - method: "POST"
    # Menggunakan variabel dari request sebelumnya
    path: "{{base_url}}/admin/delete?_token={{csrf_token}}"
    body: "id=1"
    
    # --- MATCHERS (Kondisi Temuan) ---
    matchers_condition: "and" # 'and' atau 'or'
    matchers:
      # Matcher 1: Tipe Status
      - type: "status"
        status: 200
        
      # Matcher 2: Tipe Word (Teks)
      - type: "word"
        part: "body" # Target: body, header
        words:
          - "User deleted successfully"
          - "Admin Dashboard"
        condition: "or" # 'or' atau 'and' (untuk daftar 'words')

      # Matcher 3: Tipe Regex
      - type: "regex"
        part: "body"
        regex:
          - "root:x:0:0"
        
      # Matcher 4: Tipe Binary (Hex)
      - type: "binary"
        part: "body"
        hex_payloads:
          - "474946383961" # GIF
