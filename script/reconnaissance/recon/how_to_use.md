# PANDUAN OPERASI: RECON ENGINE v12.2(Stateful Template-Based Assessment Engine)

Selamat datang di engine pemindaian v12.2. 
Anda telah berhasil membangun framework keamanan modular yang menggabungkan penemuan (discovery), crawling (perayapan), dan verifikasi kerentanan berbasis templat.Dokumen ini adalah panduan lengkap Anda untuk menggunakan alat ini, dari skenario dasar hingga alur kerja bug bounty profesional.

## ⚠️ PERINGATAN WAJIBAlat ini dirancang untuk penelitian keamanan yang sah dan diotorisasi. Ia menjalankan templat yang dapat melakukan tindakan intrusif.
- JANGAN PERNAH menjalankan alat ini terhadap domain yang tidak Anda miliki izin tertulisnya.
- ANDA BERTANGGUNG JAWAB atas templat yang Anda muat dan perintah yang Anda jalankan.
- Memindai `example.com` secara agresif adalah PELANGGARAN HUKUM dan aturan program bug bounty.
- Memindai `http://localhost:3000` (lab Anda sendiri) adalah CARA YANG BENAR.

## 📂 Instalasi & Setup

Dependensi Wajib:Pastikan Anda telah menginstal semua library Python yang diperlukan.

```bash
# Instal SEMUA dependensi (termasuk yang baru dari v12)
pip install aiohttp aiodns tqdm pyppeteer aiosqlite PyYAML lxml beautifulsoup4
```

Setup Browser Headless (Hanya Sekali):Alat ini menggunakan Pyppeteer untuk mode `--headless`. Pyppeteer perlu mengunduh browser Chromium-nya sendiri.

```bash
# Jalankan ini di terminal Anda
pyppeteer-install
```

Struktur File yang Direkomendasikan:Pastikan Anda memiliki struktur ini agar semua impor (lib.core, dll.) berfungsi.

```
recon-v12/
├── recon-v12.0.py          
├── tech_signatures.json
├── js_patterns.json
├── waf_signatures.json
├── wordlists/
│   └── common-passwords.txt
├── templates/                
│   ├── sensitive-env.yaml    
│   ├── basic-xss.yaml        
│   ├── csrf-extractor.yaml 
│   └── lfi-regex.yaml        
└── lib/
    ├── __init__.py
    ├── core.py           
    ├── auth.py           
    ├── database.py        
    ├── discovery.py     
    ├── verification.py   
    └── utils.py            
```
## Skenario Penggunaan: Dari Dasar ke Canggih

Semua perintah ini dijalankan dari dalam folder `recon-v12/`.

**Level 1: Pemindaian Dasar (HTTP Cepat)**

Tujuan: Menemukan subdomain dan direktori di target, lalu menjalankan templat sederhana.
- `-c 100`: (Concurrency) Cepat, 100 tugas sekaligus.

- `-o ./hasil_cepat`: Menyimpan laporan di folder hasil_cepat.

```bash
# Ganti subs.txt dan dirs.txt dengan wordlist Anda
python recon-v12.0.py example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 100 -o ./hasil_cepat
```

(PERINGATAN: Jangan jalankan ini di `example.com` sungguhan. Gunakan localhost.)

**Level 2: Pemindaian Aplikasi JavaScript (Headless & Rekursif)**

Tujuan: Memindai aplikasi modern (React, Vue, Angular) yang membangun halaman menggunakan JS.

- `--headless`: Menggunakan browser Chrome sungguhan (via Pyppeteer) untuk me-render JS.
- `-r`: (Recursive) Crawler akan mengikuti tautan <a> yang ditemukannya di dalam halaman.

- `-c 20`: PENTING: Konkurensi harus rendah (10-25) untuk mode headless agar tidak crash.

```bash
python recon-v12.0.py app.example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 20 -r --headless -o ./hasil_js
```

**Level 3: Pemindaian Terotentikasi (Setelah Login)**

Tujuan: Memindai area aplikasi yang dilindungi (misal: `/dashboard`) sebagai pengguna yang sudah login.

- Login ke `app.example.com` di browser Anda.
- Buka DevTools (F12) -> Application -> Cookies.

- Salin (copy) nilai cookie sesi (misal: `session_id`).

- `-b "..."`: (Cookie) Mengatur cookie otentikasi untuk semua request.

- `--silent`: Menyembunyikan output `[LIVE]` dan `[PARAM]` agar Anda hanya melihat temuan `[TEMUAN: HIGH]`.

```bash
python recon-v12.0.py app.example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 50 --silent -b "session_id=abc123xyz"
```

**Level 4: Pemindaian dengan Auto-Login & Validasi Sesi**

Tujuan: Mengotomatiskan login dan memastikan sesi tetap aktif selama pemindaian panjang.

- `--login-url`: Endpoint API untuk POST data login.

- `--login-data`: Payload POST (format kueri URL).

- `--auth-check-url`: URL yang hanya bisa diakses saat login (misal: halaman profil).

- `--auth-check-string`: Teks yang MUNCUL jika Anda LOGOUT (misal: "Please login"). Engine akan mengecek URL, dan jika menemukan string ini, ia akan mencoba login ulang.

```bash
python recon-v12.0.py example.com -t ./templates/ -sw subs.txt -dw dirs.txt -c 50 \
    --login-url "[https://example.com/api/login](https://example.com/api/login)" \
    --login-data "user=scanner&pass=ScannerPass123" \
    --auth-check-url "[https://example.com/dashboard](https://example.com/dashboard)" \
    --auth-check-string "You need to sign in"
```

**Level 5: Melanjutkan Pemindaian (Resume)**

Tujuan: Melanjutkan pemindaian yang crash atau dihentikan `(Ctrl+C)`.

Jika pemindaian 10 jam Anda gagal, Anda tidak perlu mengulang dari awal. Database (recon.db) di folder output Anda telah menyimpan semua temuan discovery.

- `--resume`: Memberi tahu engine untuk memuat data dari recon.db di folder -o.

- PENTING: Saat `--resume`, engine akan melewatkan Phase 1, 2, dan 3 (Discovery & Crawling) dan langsung lompat ke Phase 4 (Template Assessment).

```bash
# Tidak perlu -sw atau -dw lagi, karena data sudah ada di DB
python recon-v12.0.py example.com -t ./templates/ -o ./hasil_scan_lama --resume
```

## Alur Kerja Bug Bounty Profesional (Seperti Skenario Grafana)

Ini adalah cara "tertinggi" untuk menggunakan alat ini, menggabungkan semuanya:

1. Siapkan Lab Lokal: (misal: `docker run ...` Grafana di `localhost:3000`).

2. Pemetaan Manual (Burp): Login sebagai `Admin`, `Editor`, dan `Viewer`. Pahami cara kerja aplikasi dan kumpulkan endpoint sensitif (misal: `POST /api/datasources`).

3. Tulis Templat Cerdas: Buat templat (misal: `templates/viewer-create-datasource.yaml`) yang menguji bug Broken Access Control (BAC) secara spesifik.

4. Dapatkan Cookie Level Rendah: Login sebagai Viewer dan salin cookie sesinya.Eksekusi Terfokus: Jalankan pemindaian yang sangat spesifik dan terkontrol.# Buat file wordlist kosong agar Phase 1 & 3 tidak berisik

```bash
echo. > empty_subs.txt
echo. > empty_dirs.txt

# Jalankan pemindaian yang ditargetkan, terotentikasi,
# dan aman terhadap lab LOKAL Anda.
# Ganti [COOKIE_VIEWER_ANDA] dengan cookie yang valid.

python recon-v12.0.py localhost:3000 `
    -t ./templates/ `
    -sw empty_subs.txt `
    -dw empty_dirs.txt `
    -c 1 `
    --silent `
    -b "grafana_session=[COOKIE_VIEWER_ANDA]" `
    -o ./hasil_grafana_final
```