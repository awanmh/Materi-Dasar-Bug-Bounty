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
- Arsitektur Plugin: Mudah diperluas. Cukup tambahkan file `.py` baru di folder `plugins/` untuk menambahkan jenis pemindaian baru.

- Deteksi Hibrida:

    - Fase 1 (Cepat): Crawling dan pemindaian server-side (Reflected XSS, SQLi, SSRF) menggunakan `requests` secara multi-thread.

    - Fase 2 (Dalam): Pemindaian client-side (DOM-based XSS) menggunakan `Selenium Grid` secara paralel.

- Deteksi Canggih:

    - SSRF: Deteksi out-of-band (OAST) yang akurat menggunakan `Interact.sh`.

    - DOM XSS: Pengujian multi-vektor (URL Hash, LocalStorage, Window.name) yang dijalankan secara paralel.

- Manajemen Dependensi: Dikemas penuh dalam `Docker`, menghilangkan masalah "works on my machine" dan konflik dependensi.

- Skalabilitas: Pemindaian DOM XSS dapat dipercepat dengan mudah dengan menambah jumlah node browser di Selenium Grid.

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
│   L── result_manager.py    # Mengelola pencatatan, agregasi, & pelaporan hasil
|
├── plugins/                 # [PLUGIN] Berisi semua logika deteksi kerentanan.
│   ├── __init__.py          # Menjadikan 'plugins' sebagai modul Python
│   ├── plugin_dom_xss.py    # Plugin #1: Tes DOM XSS (Fase 2, Selenium)
│   ├── plugin_headers.py    # Plugin #2: Tes Header Keamanan (Fase 1, Requests)
│   ├── plugin_reflected_xss.py # Plugin #3: Tes Reflected XSS (Fase 1, Requests)
│   ├── plugin_sqli_time.py  # Plugin #4: Tes SQLi Time-based (Fase 1, Requests)
│   L── plugin_ssrf_oast.py  # Plugin #5: Tes SSRF OAST (Fase 1, Requests)
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