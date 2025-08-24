# **Modul 2: Struktur Aplikasi Web \- Membedah Anatomi Target**

## **Pendahuluan: Dari Tampilan Menjadi Vektor Serangan**

Jika Modul 1 adalah tentang memahami bagaimana data berjalan melintasi internet, Modul 2 adalah tentang membedah apa yang terjadi ketika data itu tiba di browser Anda. Modul ini akan membawa Anda dari seorang "pengguna" menjadi seorang "analis", mengubah cara Anda melihat sebuah halaman web. Di balik setiap tombol, formulir, dan teks yang Anda lihat, terdapat struktur kode yang mendefinisikan perilaku, tampilan, dan interaksi.

Bagi seorang *bug bounty hunter*, memahami struktur ini adalah seperti seorang ahli bedah yang memahami anatomi manusia. Anda harus tahu di mana "organ vital" (komponen fungsional) berada, bagaimana "sistem saraf" (JavaScript) mengontrol tindakan, dan bagaimana "aliran darah" (data) bergerak antara klien dan server. Dengan membedah anatomi aplikasi web—terdiri dari HTML, CSS, JavaScript, API, dan Database—Anda akan belajar mengidentifikasi titik-titik lemah di mana sebuah suntikan (*injection*) dapat dilakukan, logika dapat dimanipulasi, atau data dapat dicuri.

Modul ini akan membekali Anda dengan pengetahuan untuk membaca halaman web bukan sebagai konten statis, tetapi sebagai kumpulan komponen dinamis yang saling berinteraksi—setiap interaksi adalah potensi celah keamanan yang menunggu untuk ditemukan.

---

## **Bagian 1: Kerangka Halaman \- HTML dari Sudut Pandang Keamanan**

*Hypertext Markup Language* (HTML) adalah fondasi dari setiap halaman web. Ia menyediakan struktur dan makna semantik untuk konten, seperti mendefinisikan paragraf, judul, tautan, dan yang paling penting bagi seorang *hunter*, formulir input pengguna. Meskipun HTML sendiri bukanlah bahasa pemrograman, cara browser menafsirkan dan merendernya, terutama ketika dikombinasikan dengan input pengguna, menjadikannya garis depan dalam banyak serangan web.

### **1.1 Titik Masuk Data: Tag \<form\> dan \<input\>**

Hampir setiap interaksi yang berarti di web, mulai dari login, pencarian, hingga meninggalkan komentar, terjadi melalui formulir HTML. Dari perspektif keamanan, formulir adalah gerbang utama tempat data yang tidak tepercaya dari pengguna masuk ke dalam aplikasi.

* **\<form\>:** Tag ini berfungsi sebagai wadah untuk elemen-elemen input. Atribut action menentukan URL *endpoint* di server tempat data akan dikirim, dan atribut method menentukan metode HTTP yang akan digunakan (biasanya GET atau POST).1  
* **\<input\>:** Ini adalah elemen yang paling beragam, digunakan untuk mengumpulkan data pengguna. Atribut type dapat berupa text, password, hidden, submit, dll.3

Mengapa ini penting?  
Setiap elemen \<input\> adalah vektor serangan potensial. Penyerang akan selalu mencari formulir di aplikasi target untuk menguji bagaimana server menangani data yang dikirim. Apakah input divalidasi dengan benar? Apakah input disanitasi sebelum ditampilkan kembali ke pengguna lain? Jawaban atas pertanyaan-pertanyaan ini menentukan apakah kerentanan seperti HTML Injection, Cross-Site Scripting (XSS), atau bahkan SQL Injection mungkin terjadi.5

### **1.2 Pedang Bermata Dua: Tag \<script\>**

Tag \<script\> digunakan untuk menyematkan atau merujuk ke kode JavaScript yang dapat dieksekusi. Tanpa tag ini, web modern yang dinamis dan interaktif tidak akan ada. Namun, kemampuan untuk mengeksekusi kode inilah yang menjadikannya target utama dalam serangan injeksi.

Ketika sebuah aplikasi gagal membersihkan input pengguna dengan benar dan memasukkannya ke dalam halaman HTML, seorang penyerang dapat menyuntikkan tag \<script\> mereka sendiri.5

Contoh sederhana:

HTML
```
\<div\>Selamat datang, \<script\>alert('XSS')\</script\>\!\</div\>
```
Jika aplikasi merender ini secara langsung, browser akan mengeksekusi kode di dalam tag \<script\>, memunculkan kotak peringatan. Ini adalah bukti konsep (PoC) klasik untuk Cross-Site Scripting (XSS).8 Meskipun

alert() itu sendiri tidak berbahaya, itu membuktikan bahwa penyerang dapat menjalankan JavaScript sewenang-wenang di browser korban, yang dapat digunakan untuk mencuri *cookie* sesi, merekam ketikan keyboard, atau memanipulasi konten halaman.

---

## **Bagian 2: Memberi Gaya \- Peran Singkat CSS**

*Cascading Style Sheets* (CSS) adalah bahasa yang digunakan untuk mendeskripsikan presentasi atau gaya sebuah dokumen yang ditulis dalam HTML.9 Ini mengontrol warna, font, tata letak, dan aspek visual lainnya.

Bagi seorang *bug bounty hunter*, CSS umumnya bukan fokus utama. Kerentanan yang berasal murni dari CSS sangat jarang dan kompleks. Namun, penting untuk mengetahui bahwa dalam skenario tertentu, CSS dapat digunakan sebagai bagian dari rantai serangan, misalnya untuk membocorkan data sensitif (seperti token CSRF) melalui properti CSS yang dibuat secara dinamis atau untuk membantu dalam serangan *UI redressing* (clickjacking). Untuk saat ini, cukup pahami bahwa CSS bertanggung jawab atas "tampilan", sementara HTML adalah "struktur" dan JavaScript adalah "perilaku".

---

## **Bagian 3: Membuat Halaman Menjadi Hidup \- JavaScript & DOM**

JavaScript adalah bahasa pemrograman yang berjalan di browser klien. Ia mengubah halaman HTML statis menjadi aplikasi yang dinamis dan interaktif. Untuk melakukannya, JavaScript berinteraksi dengan representasi internal halaman di memori browser, yang dikenal sebagai DOM.

### **3.1 Struktur Logis Halaman: DOM (Document Object Model)**

Ketika browser memuat halaman web, ia membuat model terstruktur dari dokumen tersebut yang disebut *Document Object Model* (DOM). DOM merepresentasikan halaman sebagai pohon objek, di mana setiap tag HTML adalah sebuah "simpul" (*node*).10 JavaScript dapat membaca, menambah, menghapus, atau memodifikasi simpul-simpul ini, yang secara dinamis mengubah apa yang dilihat pengguna tanpa perlu memuat ulang halaman.

### **3.2 Pemicu Aksi: *Event* JavaScript**

*Event* adalah tindakan atau kejadian yang terjadi di dalam sistem, yang dapat dideteksi dan direspons oleh kode. Ini bisa berupa interaksi pengguna (seperti onclick, onmouseover), atau kejadian browser (seperti onload, onerror).13 Penyerang sering menyalahgunakan

*event handler* ini untuk mengeksekusi *payload* XSS mereka.

Contoh payload XSS yang menggunakan *event handler* onerror:

HTML
```
\<img src\="x" onerror\="alert('XSS')"\>
```

Browser akan mencoba memuat gambar dari sumber yang tidak valid (x), yang akan memicu *event* onerror, dan kemudian mengeksekusi kode JavaScript yang ditentukan.

### **3.3 "Hello, World\!" Keamanan: Fungsi alert()**

Fungsi alert() di JavaScript menampilkan kotak dialog sederhana dengan pesan.15 Dalam konteks

*bug bounty*, alert(1) atau alert(document.domain) adalah cara standar dan universal untuk menunjukkan bukti konsep (PoC) bahwa Anda telah berhasil mengeksekusi JavaScript di halaman target. Ini tidak berbahaya, mudah dikenali, dan secara definitif membuktikan adanya kerentanan XSS.

Kombinasi dari manipulasi DOM melalui JavaScript yang dipicu oleh *event* adalah inti dari **DOM-based XSS**. Dalam serangan ini, *payload* penyerang tidak pernah dikirim ke server. Sebaliknya, skrip sisi klien yang rentan mengambil data dari sumber yang dapat dikontrol (seperti URL) dan menuliskannya ke DOM, yang kemudian dieksekusi oleh browser.

---

## **Bagian 4: Jembatan ke Server \- API & REST**

Aplikasi web modern jarang memuat seluruh halaman dari awal. Sebaliknya, mereka sering menggunakan *Application Programming Interfaces* (API) untuk mengambil atau mengirim data secara asinkron di latar belakang. Arsitektur API yang paling umum digunakan di web adalah REST (*Representational State Transfer*).

REST bukanlah protokol yang kaku, melainkan seperangkat prinsip arsitektur yang menggunakan metode HTTP standar untuk berinteraksi dengan sumber daya (*resources*). Setiap metode HTTP memiliki makna spesifik yang sering dipetakan ke operasi CRUD (Create, Read, Update, Delete).

* **GET (Read):** Mengambil data dari sumber daya. Misalnya, GET /api/users/123 akan mengambil detail pengguna dengan ID 123\. Seharusnya ini adalah operasi yang aman dan idempoten (menjalankannya berkali-kali tidak mengubah status server).  
* **POST (Create):** Mengirim data untuk membuat sumber daya baru. Misalnya, POST /api/users dengan detail pengguna di *body* permintaan akan membuat pengguna baru. Operasi ini tidak idempoten (menjalankannya berkali-kali akan membuat banyak pengguna baru).  
* **PUT (Update/Replace):** Mengirim data untuk memperbarui sumber daya yang ada secara keseluruhan. Misalnya, PUT /api/users/123 akan menggantikan seluruh data pengguna 123 dengan data baru yang dikirim. Operasi ini idempoten.  
* **DELETE (Delete):** Menghapus sumber daya yang ada. Misalnya, DELETE /api/users/123 akan menghapus pengguna 123\. Operasi ini juga idempoten.

Bagi seorang *bug hunter*, API adalah permukaan serangan yang sangat kaya. Anda harus menguji apakah kontrol akses diterapkan dengan benar di setiap *endpoint* dan untuk setiap metode. Apakah pengguna biasa dapat mengirim permintaan DELETE ke *endpoint* admin? Apakah Anda dapat mengubah ID pengguna dalam permintaan GET untuk melihat data pengguna lain (kerentanan IDOR)? Memahami REST dan metode HTTP adalah kunci untuk menguji logika bisnis dan kontrol akses aplikasi.

---

## **Bagian 5: Gudang Data \- Konsep Dasar Query SQL**

Di balik sebagian besar aplikasi web, terdapat sebuah database yang menyimpan semua data: informasi pengguna, produk, postingan blog, dll. Bahasa yang paling umum digunakan untuk berkomunikasi dengan database relasional adalah **SQL (Structured Query Language)**.

Sebagai seorang *bug hunter*, Anda tidak perlu menjadi seorang administrator database, tetapi Anda harus memahami konsep dasar dari query SQL, terutama yang berkaitan dengan manipulasi data (DML \- Data Manipulation Language).

* **SELECT:** Perintah untuk **membaca** atau mengambil data. Ini adalah perintah yang paling umum.  
  SQL
  ```  
  SELECT username, email FROM users WHERE user\_id \= 1;
  ```
* **INSERT:** Perintah untuk **membuat** atau menambahkan data baru.  
  SQL
  ```  
  INSERT INTO users (username, password) VALUES ('hunter', 'pa$$w0rd');
  ```
* **UPDATE:** Perintah untuk **memperbarui** data yang sudah ada.  
  SQL
  ```  
  UPDATE users SET password \= 'new\_password' WHERE username \= 'hunter';
  ```
* **DELETE:** Perintah untuk **menghapus** data.  
  SQL
  ```  
  DELETE FROM users WHERE username \= 'hunter';
  ```
  
Penting untuk memahami bahwa input dari pengguna (misalnya, dari formulir login atau bilah pencarian) seringkali digunakan untuk membangun query-query ini secara dinamis di *backend*. Jika input ini tidak ditangani dengan hati-hati, penyerang dapat menyisipkan sintaks SQL mereka sendiri untuk memanipulasi query asli. Ini adalah dasar dari kerentanan **SQL Injection**, yang akan dibahas secara mendalam di modul berikutnya.

---

## **Bagian 6: Latihan Praktis \- Membedah Aplikasi di Lingkungan Aman**

Teori saja tidak cukup. Cara terbaik untuk memahami struktur aplikasi web adalah dengan membedahnya sendiri. Gunakan lingkungan yang dirancang khusus untuk latihan keamanan agar Anda dapat bereksperimen secara legal dan aman.

**Platform yang Direkomendasikan:**

* **PortSwigger Web Security Academy:** Sumber daya gratis dan komprehensif dengan puluhan lab interaktif yang mencakup hampir setiap jenis kerentanan web. Ini adalah standar industri untuk belajar.  
* **DVWA (Damn Vulnerable Web App):** Aplikasi web PHP/MySQL yang sengaja dibuat rentan. Anda dapat meng-host-nya secara lokal untuk berlatih menemukan dan mengeksploitasi kerentanan umum.

### **Latihan 1: Mengamati Permintaan POST dari Formulir**

1. **Siapkan Alat:** Pastikan Burp Suite Anda berjalan dan browser Anda dikonfigurasi untuk menggunakan *proxy* Burp (seperti yang dibahas di Modul 1).  
2. **Buka Target:** Buka halaman login di DVWA atau salah satu lab login di PortSwigger Academy.  
3. **Matikan Intercept:** Di Burp, buka tab Proxy \> Intercept dan pastikan tombolnya bertuliskan Intercept is off.  
4. **Kirim Data:** Di browser, isi formulir login dengan data apa pun (misalnya, test:test) dan klik tombol login/submit.  
5. **Analisis Riwayat:** Beralih ke Burp Suite dan buka tab Proxy \> HTTP history. Anda akan melihat daftar semua permintaan yang dibuat oleh browser Anda. Cari permintaan POST ke *endpoint* login (misalnya, /login.php).  
6. **Inspeksi Permintaan:** Klik pada permintaan tersebut. Di panel bawah, lihat tab Request. Perhatikan bagaimana data yang Anda masukkan di formulir (test:test) dikirim di bagian *body* dari permintaan POST. Ini adalah data yang diterima server.

### **Latihan 2: Memanipulasi Parameter dengan Burp Repeater**

1. **Kirim ke Repeater:** Di tab HTTP history, klik kanan pada permintaan POST yang Anda temukan di latihan sebelumnya dan pilih Send to Repeater.  
2. **Buka Repeater:** Buka tab Repeater. Anda akan melihat permintaan POST yang sama, siap untuk dimodifikasi dan dikirim ulang.  
3. **Ubah Parameter:** Di panel Request di sebelah kiri, ubah salah satu nilai parameter. Misalnya, jika ada parameter username=test, ubah menjadi username=admin.  
4. **Kirim Ulang:** Klik tombol Send.  
5. **Analisis Respons:** Respons dari server akan muncul di panel Response di sebelah kanan. Bandingkan respons ini dengan respons asli yang Anda lihat di HTTP history. Apakah ada pesan kesalahan yang berbeda? Apakah halaman merespons secara berbeda? Proses memodifikasi parameter dan menganalisis respons ini adalah inti dari pengujian manual.

---

## **Kesimpulan**

Anda sekarang telah membedah lapisan-lapisan dasar yang membentuk aplikasi web. Anda tahu bahwa HTML adalah kerangka, JavaScript adalah otot dan saraf, API adalah jembatan komunikasi, dan database adalah otaknya. Setiap komponen ini, dan cara mereka berinteraksi, menciptakan permukaan serangan yang luas. Dengan pemahaman ini, Anda siap untuk beralih dari sekadar mengidentifikasi komponen ke menemukan dan mengeksploitasi kerentanan yang ada di dalamnya, yang akan menjadi fokus dari modul-modul berikutnya.

---

## **Referensi**

* 1  
  [https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/form](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/form)  
* 2  
  [https://www.w3.org/TR/html401/interact/forms.html](https://www.w3.org/TR/html401/interact/forms.html)  
* 3  
  [https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input)  
* 4  
  [https://devdoc.net/web/developer.mozilla.org/en-US/docs/Web/HTML/Element/input.html](https://devdoc.net/web/developer.mozilla.org/en-US/docs/Web/HTML/Element/input.html)  
* 17  
  [https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script)  
* 18  
  [https://developer.mozilla.org/en-US/docs/Web/API/HTMLScriptElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLScriptElement)  
* 5  
  [https://www.imperva.com/learn/application-security/html-injection/](https://www.imperva.com/learn/application-security/html-injection/)  
* 6  
  [https://www.acunetix.com/vulnerabilities/web/html-injection/](https://www.acunetix.com/vulnerabilities/web/html-injection/)  
* 7  
  [https://portswigger.net/kb/issues/00200300\_cross-site-scripting-reflected](https://portswigger.net/kb/issues/00200300_cross-site-scripting-reflected)  
* 8  
  [https://portswigger.net/web-security/cross-site-scripting](https://portswigger.net/web-security/cross-site-scripting)  
* 9  
  [https://developer.mozilla.org/en-US/docs/Web/CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)  
* 10  
  [https://en.wikipedia.org/wiki/Document\_Object\_Model](https://en.wikipedia.org/wiki/Document_Object_Model)  
* 11  
  [https://udn.realityripple.com/docs/Glossary/DOM](https://udn.realityripple.com/docs/Glossary/DOM)  
* 12  
  [https://developer.mozilla.org/en-US/docs/Web/API/Document\_Object\_Model/Introduction](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)  
* 14  
  [https://developer.mozilla.org/en-US/docs/Learn\_web\_development/Core/Scripting/Events](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events)  
* 13  
  [https://developer.mozilla.org/en-US/docs/Web/API/Document\_Object\_Model/Events](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Events)  
* 15  
  [https://developer.mozilla.org/en-US/docs/Web/API/Window/alert](https://developer.mozilla.org/en-US/docs/Web/API/Window/alert)  
* 16  
  [https://www.geeksforgeeks.org/html/html-dom-window-alert-method/](https://www.geeksforgeeks.org/html/html-dom-window-alert-method/)  
* 19  
  [https://owasp.org/www-community/attacks/DOM\_Based\_XSS](https://owasp.org/www-community/attacks/DOM_Based_XSS)  
* 20  
  [https://owasp.org/www-project-web-security-testing-guide/v41/4-Web\_Application\_Security\_Testing/11-Client\_Side\_Testing/01-Testing\_for\_DOM-based\_Cross\_Site\_Scripting](https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/11-Client_Side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting)  
* 21  
  [https://www.kali.org/tools/dvwa/](https://www.kali.org/tools/dvwa/)  
* 22  
  [https://en.wikipedia.org/wiki/Damn\_Vulnerable\_Web\_Application](https://en.wikipedia.org/wiki/Damn_Vulnerable_Web_Application)  
* 23  
  [https://portswigger.net/web-security](https://portswigger.net/web-security)  
* [https://support.microsoft.com/id-id/topic/access-sql-konsep-dasar-kosakata-dan-sintaks-444d0303-cde1-424e-9a74-e8dc3e460671](https://support.microsoft.com/id-id/topic/access-sql-konsep-dasar-kosakata-dan-sintaks-444d0303-cde1-424e-9a74-e8dc3e460671)  
* [https://diengcyber.com/sql-3/](https://diengcyber.com/sql-3/)  
* [https://www.fanruan.com/id/blog/sql](https://www.fanruan.com/id/blog/sql)  
* [https://it.telkomuniversity.ac.id/perintah-dasal-sql/](https://it.telkomuniversity.ac.id/perintah-dasal-sql/)  
* [https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/](https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/)  
* [https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/](https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/)  
* [https://csirt.teknokrat.ac.id/belajar-sql-cara-cepat-kuasai-query-dasar/](https://csirt.teknokrat.ac.id/belajar-sql-cara-cepat-kuasai-query-dasar/)  
* [https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/](https://nevacloud.com/blog/query-sql-dari-a-z-definisi-contoh-hingga-cara-hindari-error/)  
* [https://www.reddit.com/r/learnprogramming/comments/zrzyyu/understanding\_crud\_rest\_api\_get\_put\_post\_delete/](https://www.reddit.com/r/learnprogramming/comments/zrzyyu/understanding_crud_rest_api_get_put_post_delete/)  
* 5  
  [https://www.imperva.com/learn/application-security/html-injection/](https://www.imperva.com/learn/application-security/html-injection/)  
* [https://restfulapi.net/http-methods/](https://restfulapi.net/http-methods/)  
* [https://rhashibur75.medium.com/html-injection-bug-bounty-a41f87217118](https://rhashibur75.medium.com/html-injection-bug-bounty-a41f87217118)  
* [https://rhashibur75.medium.com/html-injection-bug-bounty-a41f87217118](https://rhashibur75.medium.com/html-injection-bug-bounty-a41f87217118)  
* [https://medium.com/@NiaziSec/bug-bounty-hunting-web-vulnerability-api-testing-96a49acc4f35](https://medium.com/@NiaziSec/bug-bounty-hunting-web-vulnerability-api-testing-96a49acc4f35)  
* [https://medium.com/@NiaziSec/bug-bounty-hunting-web-vulnerability-api-testing-96a49acc4f35](https://medium.com/@NiaziSec/bug-bounty-hunting-web-vulnerability-api-testing-96a49acc4f35)  
* [https://uploadcare.com/blog/vulnerability-in-html-design/](https://uploadcare.com/blog/vulnerability-in-html-design/)  
* [https://allenlopes23.medium.com/the-hidden-danger-unveiling-html-injection-in-contact-us-forms-8b57b737030a](https://allenlopes23.medium.com/the-hidden-danger-unveiling-html-injection-in-contact-us-forms-8b57b737030a)  
* 13  
  [https://developer.mozilla.org/en-US/docs/Web/API/Document\_Object\_Model/Events](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Events)  
* [https://www.yeswehack.com/learn-bug-bounty/javascript-language-made-for-bugs](https://www.yeswehack.com/learn-bug-bounty/javascript-language-made-for-bugs)  
* [https://www.yeswehack.com/learn-bug-bounty/javascript-language-made-for-bugs](https://www.yeswehack.com/learn-bug-bounty/javascript-language-made-for-bugs)  
* [https://api7.ai/learning-center/api-101/http-methods-in-apis](https://api7.ai/learning-center/api-101/http-methods-in-apis)  
* [https://www.reddit.com/r/HowToHack/comments/j1ytxm/how\_good\_is\_portswigger\_academy/](https://www.reddit.com/r/HowToHack/comments/j1ytxm/how_good_is_portswigger_academy/)  
* [https://www.reddit.com/r/HowToHack/comments/j1ytxm/how\_good\_is\_portswigger\_academy/](https://www.reddit.com/r/HowToHack/comments/j1ytxm/how_good_is_portswigger_academy/)  
* [https://medium.com/@robinthehood257/bug-bounty-journey-43494e2c498b](https://medium.com/@robinthehood257/bug-bounty-journey-43494e2c498b)  
* [https://research.securitum.com/art-of-bug-bounty-a-way-from-js-file-analysis-to-xss/](https://research.securitum.com/art-of-bug-bounty-a-way-from-js-file-analysis-to-xss/)  
* [https://portswigger.net/web-security/cross-site-scripting/dom-based](https://portswigger.net/web-security/cross-site-scripting/dom-based)

#### **Karya yang dikutip**

1.   
2. Forms in HTML documents \- W3C, diakses Agustus 24, 2025, [https://www.w3.org/TR/html401/interact/forms.html](https://www.w3.org/TR/html401/interact/forms.html)  
3. : The HTML Input element \- MDN, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input)  
4. \- HTML | MDN \- Developer's Documentation Collections, diakses Agustus 24, 2025, [https://devdoc.net/web/developer.mozilla.org/en-US/docs/Web/HTML/Element/input.html](https://devdoc.net/web/developer.mozilla.org/en-US/docs/Web/HTML/Element/input.html)  
5. What Is HTML Injection | Types, Risks & Mitigation Techniques ..., diakses Agustus 24, 2025, [https://www.imperva.com/learn/application-security/html-injection/](https://www.imperva.com/learn/application-security/html-injection/)  
6. HTML Injection \- Vulnerabilities \- Acunetix, diakses Agustus 24, 2025, [https://www.acunetix.com/vulnerabilities/web/html-injection/](https://www.acunetix.com/vulnerabilities/web/html-injection/)  
7. Cross-site scripting (reflected) \- PortSwigger, diakses Agustus 24, 2025, [https://portswigger.net/kb/issues/00200300\_cross-site-scripting-reflected](https://portswigger.net/kb/issues/00200300_cross-site-scripting-reflected)  
8. What is cross-site scripting (XSS) and how to prevent it? | Web ..., diakses Agustus 24, 2025, [https://portswigger.net/web-security/cross-site-scripting](https://portswigger.net/web-security/cross-site-scripting)  
9. CSS: Cascading Style Sheets \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)  
10. Document Object Model \- Wikipedia, diakses Agustus 24, 2025, [https://en.wikipedia.org/wiki/Document\_Object\_Model](https://en.wikipedia.org/wiki/Document_Object_Model)  
11. DOM (Document Object Model) \- MDN Web Docs Glossary: Definitions of Web-related terms, diakses Agustus 24, 2025, [https://udn.realityripple.com/docs/Glossary/DOM](https://udn.realityripple.com/docs/Glossary/DOM)  
12. Introduction to the DOM \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/API/Document\_Object\_Model/Introduction](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction)  
13. DOM events \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/API/Document\_Object\_Model/Events](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Events)  
14. Introduction to events \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Learn\_web\_development/Core/Scripting/Events](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/Events)  
15. Window: alert() method \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/API/Window/alert](https://developer.mozilla.org/en-US/docs/Web/API/Window/alert)  
16. HTML DOM Window alert() Method \- GeeksforGeeks, diakses Agustus 24, 2025, [https://www.geeksforgeeks.org/html/html-dom-window-alert-method/](https://www.geeksforgeeks.org/html/html-dom-window-alert-method/)  
17.   
18. HTMLScriptElement \- MDN \- Mozilla, diakses Agustus 24, 2025, [https://developer.mozilla.org/en-US/docs/Web/API/HTMLScriptElement](https://developer.mozilla.org/en-US/docs/Web/API/HTMLScriptElement)  
19. DOM Based XSS | OWASP Foundation, diakses Agustus 24, 2025, [https://owasp.org/www-community/attacks/DOM\_Based\_XSS](https://owasp.org/www-community/attacks/DOM_Based_XSS)  
20. Testing for DOM-Based Cross Site Scripting \- WSTG \- v4.1 | OWASP Foundation, diakses Agustus 24, 2025, [https://owasp.org/www-project-web-security-testing-guide/v41/4-Web\_Application\_Security\_Testing/11-Client\_Side\_Testing/01-Testing\_for\_DOM-based\_Cross\_Site\_Scripting](https://owasp.org/www-project-web-security-testing-guide/v41/4-Web_Application_Security_Testing/11-Client_Side_Testing/01-Testing_for_DOM-based_Cross_Site_Scripting)  
21. dvwa | Kali Linux Tools, diakses Agustus 24, 2025, [https://www.kali.org/tools/dvwa/](https://www.kali.org/tools/dvwa/)  
22. Damn Vulnerable Web Application \- Wikipedia, diakses Agustus 24, 2025, [https://en.wikipedia.org/wiki/Damn\_Vulnerable\_Web\_Application](https://en.wikipedia.org/wiki/Damn_Vulnerable_Web_Application)  
23. Web Security Academy: Free Online Training from PortSwigger, diakses Agustus 24, 2025, [https://portswigger.net/web-security](https://portswigger.net/web-security)
