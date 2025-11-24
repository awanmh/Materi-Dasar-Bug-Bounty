```markdown
   ▄▄▄       ██▓███  ▓█████  ██▀███   ▒█████   ██▓    
  ▒████▄    ▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒▓██▒    
  ▒██  ▀█▄  ▓██░ ██▓▒▒███   ▓██ ░▄█ ▒▒██░  ██▒▒██░    
  ░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░▒██░    
   ▓█   ▓██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒░ ████▓▒░░██████▒
   ▒▒   ▓▒█░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▓  ░
    ▒   ▒▒ ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░ ▒  ░
    ░   ▒   ░░          ░     ░░   ░ ░ ░ ░ ▒    ░ ░   
        ░  ░            ░  ░   ░         ░ ░      ░  ░

```
## 🦈 Apex SQLi Hunter v8.0 (The Apex Predator)

**Apex SQLi Hunter** adalah mesin pemindai keamanan SQL Injection generasi terbaru yang dirancang untuk presisi mutlak. Berbeda dengan *scanner* konvensional yang mengandalkan panjang konten (*Content Length*)—yang sering gagal pada halaman dinamis—Apex v8 menggunakan algoritma **Smart Diffing (Fuzzy Logic)** untuk membedakan antara halaman normal, dinamis, dan respons injeksi dengan akurasi 99%.

Alat ini dibangun untuk *Bug Bounty Hunters* dan *Penetration Testers* yang membutuhkan kecepatan, ketepatan, dan kemampuan untuk menghindari deteksi WAF dasar.

## ⚠️ Disclaimer (Peringatan Keras)

**ALAT INI HANYA UNTUK TUJUAN PENDIDIKAN DAN PENGUJIAN LEGAL.**
Penggunaan alat ini untuk menyerang target tanpa izin tertulis adalah **ILEGAL**. Pengembang tidak bertanggung jawab atas segala kerusakan atau penyalahgunaan yang disebabkan oleh alat ini. Gunakan dengan bijak dan etis.

-----

## 🚀 Fitur "God Mode" (v8 Highlights)

### 1\. 🧠 Smart Diff Engine (Fuzzy Logic)

Tidak lagi terkecoh oleh iklan dinamis, jam digital, atau token CSRF yang berubah-ubah.

  * **Old Tech:** Mengandalkan `Content-Length`. (Banyak *False Positive*).
  * **Apex v8:** Menggunakan `difflib` untuk menghitung **Similarity Ratio**. Jika halaman berubah tapi kemiripannya masih 98%, alat ini tahu itu aman. Injeksi dideteksi hanya jika struktur halaman berubah drastis akibat manipulasi SQL.

### 2\. 🛡️ Advanced WAF Evasion

Dirancang untuk menyusup di bawah radar.

  * **IP Spoofing:** Melakukan *Header Pollution* (`X-Originating-IP`, `X-Forwarded-For`) dengan IP palsu acak di setiap permintaan untuk membingungkan *rate limiter*.
  * **Browser Mimicry:** Mengirim header lengkap (`Upgrade-Insecure-Requests`, `Accept-Language`) agar terlihat seperti pengguna browser asli.

### 3\. ✅ Auto-Verification Mechanism

Menghilangkan *False Positive* pada *Time-Based Blind*.

  * Jika server *timeout*, Apex v8 tidak langsung menyimpulkan kerentanan. Ia melakukan verifikasi ulang (`double-check`). Hanya jika permintaan kedua juga tertunda sesuai waktu yang ditentukan, kerentanan dikonfirmasi.

### 4\. 🌍 Universal DBMS Support

Tidak hanya MySQL. Mendukung payload untuk:

  * MySQL / MariaDB
  * PostgreSQL
  * Microsoft SQL Server (MSSQL)
  * Oracle
  * SQLite (Simulasi *Heavy Query*)

### 5\. 💉 Auto-Exploitation (PoC)

Jika kerentanan *Error-Based* ditemukan, alat ini secara otomatis mengekstraksi data vital (Versi DB, User, atau Nama DB) sebagai Bukti Konsep (Proof of Concept) instan.

-----

## 📦 Instalasi

Alat ini membutuhkan Python 3.x dan beberapa pustaka eksternal.

```bash
# 1. Clone atau download script ini
# 2. Install dependencies
pip install requests colorama
```

*Catatan: `difflib`, `argparse`, dan `threading` adalah pustaka standar Python dan tidak perlu diinstal.*

-----

## 📖 Cara Penggunaan

Apex v8 mendukung dua mode operasi: **Mode CLI (Pro)** untuk integrasi cepat, dan **Mode Interaktif (Pemula)**.

### 1\. Mode CLI (Command Line Interface)

Cocok untuk *scripting* atau penggunaan cepat.

**Scan target GET sederhana:**

```bash
python apex_sqli.py -u "http://target-site.com/news.php?id=1"
```

**Scan target dengan parameter POST:**

```bash
python apex_sqli.py -u "http://target-site.com/login.php" -p "username=admin&password=123"
```

### 2\. Mode Interaktif

Cukup jalankan script tanpa argumen, dan wizard akan memandu Anda.

```bash
python apex_sqli.py
```

*Output:*

```text
Masukkan URL Target: http://testphp.vulnweb.com/artists.php?artist=1
Tidak ada param GET. Mode POST? (y/n): n
... Memulai scan ...
```

-----

## 📊 Memahami Laporan Output

Warna indikator membantu Anda membaca situasi dengan cepat:

  * 🔵 **[INFO]**: Informasi proses (memulai scan, kalibrasi).
  * 🟢 **[+]**: Target aman atau pengecekan berhasil (Baseline OK).
  * 🟣 **[\!]**: Peringatan (Server lambat, potensi timeout).
  * 🔴 **[\!\!\!]**: **VULNERABILITY FOUND\!** (Kerentanan terkonfirmasi).

**Contoh Output Sukses:**

```text
[*] Scanning Target: http://testphp.vulnweb.com/artists.php?artist=1
[*] Melakukan kalibrasi Heuristic & Baseline...
[+] Baseline OK. Latency: 0.23s. Size: 4520 bytes.
[*] Testing Boolean-Based (Smart Diff)...
[!!!] Boolean SQLi Ditemukan! (Diff Logic)
[!!!] Payload True: ' AND 1=1-- - (Sim: 0.99)
[!!!] Payload False: ' AND 1=2-- - (Sim: 0.85)
[*] Testing Time-Based Blind...
[*] Mencoba Eksploitasi Data (Error-Based)...
[!!!] DATA EXFILTRATED (MySQL): root@localhost
```

-----

## 🧠 Logika Teknis (How it Works)

1.  **Calibration:** Mengambil *Baseline Request* untuk mempelajari struktur HTML normal dan latensi jaringan rata-rata.
2.  **Diffing Attack:** Menyuntikkan payload `TRUE` dan `FALSE`.
      * Jika `TRUE` ≈ Baseline (\>95% mirip) DAN `FALSE` ≠ Baseline (\<95% mirip) =\> **VULNERABLE**.
3.  **Latency Attack:** Menyuntikkan payload waktu (`SLEEP`, `WAITFOR`).
      * Jika respons \> (waktu tidur + latensi normal) DAN terverifikasi 2x =\> **VULNERABLE**.
4.  **Auto-Pwn:** Jika rentan, mencoba payload `EXTRACTVALUE` atau error-conversion untuk mencuri data versi/user.

-----

## 🛠️ Opsi Konfigurasi (Dalam Script)

Anda dapat mengedit bagian atas script untuk menyesuaikan kebutuhan:

```python
# --- KONFIGURASI GLOBAL ---
PROXY = None  # Ganti dengan {'http': 'http://127.0.0.1:8080'} untuk Burp Suite
TIMEOUT = 20  # Detik sebelum timeout
MAX_THREADS = 10 # Jumlah thread paralel
SIMILARITY_THRESHOLD = 0.95 # Sensitivitas Smart Diff (0.0 - 1.0)
```

-----

**Happy Hacking & Stay Legal\!** 🕵️‍♂️💻
