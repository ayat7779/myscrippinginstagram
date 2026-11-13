# 📝 Dokumentasi & Log Pembuatan Aplikasi (APPS.md)

Dokumen ini mencatat seluruh arsitektur, alur proses pembuatan, struktur modul, serta riwayat perubahan (changelog) untuk proyek **Instagram Web Scraper & Media Downloader**.

---

## 📌 1. Ikhtisar Aplikasi

- **Nama Aplikasi**: Instagram Web Scraper & Media Downloader
- **Teknologi Utama**: Python 3.8+, Streamlit (Web UI), Instaloader (Scraping Engine), Pandas & OpenPyXL (Data Processing), Requests (Media Download).
- **Jenis Aplikasi**: Web Application (Interaktif & Desktop-friendly).
- **Lokasi Project**: `E:/ApplicationProject/PythonApp/ScrappingInstagram/`

---

## 🏗️ 2. Arsitektur & Struktur Modul

Proyek ini dirancang dengan pendekatan modular agar mudah dikembangkan dan dipelihara:

```
ScrappingInstagram/
├── app.py              # Front-end UI (Streamlit Web App)
├── scraper.py          # Core Engine Scraping & HTTP Handling
├── exporter.py         # Data Converter (CSV, JSON, Excel) & ZIP Builder
├── requirements.txt    # Daftar dependensi Python
├── README.md           # Panduan penggunaan singkat
└── APPS.md             # Dokumentasi proses pembuatan & log perubahan (File Ini)
```

### Penjelasan Detail Modul:

1. **[app.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/app.py)**
   - Bertindak sebagai antarmuka pengguna berbasis web (Streamlit).
   - Menyediakan 3 Tab Utama:
     - **Tab 1: Scrape Profil & Postingan**: Input username, statistik profil, tabel data postingan, galeri thumbnail preview, dan tombol ekspor data/media.
     - **Tab 2: Downloader Media & Reels**: Input URL/Shortcode postingan, preview gambar/video, dan tombol download langsung (`.jpg`/`.mp4`).
     - **Tab 3: Scrape Hashtag**: Input hashtag, tabel hasil scraping postingan publik, dan tombol ekspor.
   - **Sidebar**: Autentikasi akun Instagram (opsional) untuk menghindari *rate limiting* dan pengatur jumlah batas postingan (*Max Posts slider*).

2. **[scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py)**
   - Berisi kelas `InstagramScraper` yang membungkus pustaka `instaloader`.
   - **Fungsi Utama**:
     - `get_profile_info(username)`: Mengambil metadata profil (Bio, followers, following, posts count, status private/verified, URL foto profil).
     - `scrape_profile_posts(username, max_posts, progress_callback)`: Mengambil postingan profil publik/terautentikasi.
     - `scrape_hashtag_posts(hashtag, max_posts, progress_callback)`: Mengambil postingan publik berdasarkan hashtag.
     - `get_post_by_shortcode_or_url(input_str)`: Mengambil detail 1 postingan/reel berdasarkan link atau shortcode.
     - `download_file_bytes(url)`: Mengunduh konten biner gambar/video dengan User-Agent valid.

3. **[exporter.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/exporter.py)**
   - Menyediakan utilitas untuk mengolah dan mengekspor data:
     - `export_to_csv(data)`: Mengonversi DataFrame/Dict ke format CSV dengan encoding `utf-8-sig`.
     - `export_to_json(data)`: Mengonversi data ke format JSON formatted.
     - `export_to_excel(data)`: Mengonversi data ke spreadsheet Excel `.xlsx` menggunakan `openpyxl`.
     - `create_media_zip(media_items, download_func)`: Menggabungkan beberapa file media ke dalam satu arsip `.zip` langsung di memori (`io.BytesIO`).

4. **[requirements.txt](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/requirements.txt)**
   - Pustaka pendukung:
     - `streamlit>=1.30.0`
     - `instaloader>=4.10.0`
     - `pandas>=2.0.0`
     - `openpyxl>=3.1.0`
     - `requests>=2.31.0`
     - `Pillow>=10.0.0`

---

## 📋 3. Fitur Utama Aplikasi

- [x] **Scrape Profil**: Mengambil metadata profil dan daftar postingan (Foto, Video, Caption, Likes, Comments, Timestamp).
- [x] **Download Media & Reels**: Pengunduhan media individual dari URL/Shortcode postingan.
- [x] **Scrape Hashtag**: Pencarian dan ekstraksi postingan berdasarkan Hashtag.
- [x] **Ekspor Multi-Format**: Mendukung CSV, JSON, dan Excel (.xlsx).
- [x] **Bulk Media Downloader (ZIP)**: Mengunduh seluruh media postingan yang discrape sekaligus dalam 1 file ZIP.
- [x] **Opsi Autentikasi Sesi**: Input login akun IG opsional untuk stabilitas scraping dan bypass rate limit.

---

## 🔄 4. Riwayat Perubahan (Changelog)

### **v1.3.8** *(Request Throttling & HTTP 429 Prevention)*
- **Jeda Halus HTTP Request**: Menambahkan jeda waktu `time.sleep(0.5)` pada iterator `scrape_profile_posts()` di [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L170) untuk mencegah pemicuan deteksi spam/IP rate limiting `HTTP 429` saat mengambil postingan secara berurutan.
- **Panduan Solusi HTTP 429**: Menyusun panduan 3 opsi solusi komprehensif (Gunakan `sessionid` Cookie, Ganti Jaringan/Hotspot HP, atau Tunggu Cooldown IP 15 menit).

### **v1.3.7** *(Automatic URL Unquoting for Session Cookie & Full Cookie String Support)*
- **Penguraian URL Cookie Otomatis**: Pada [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L50), ditambahkan `urllib.parse.unquote()` untuk otomatis mengurai karakter `%3A` menjadi titik dua `:` pada cookie `sessionid` yang disalin langsung dari browser/URL.
- **Header Resmi Instagram Web**: Menambahkan header `X-IG-App-ID: 936619743392459` dan `X-Requested-With: XMLHttpRequest` serta cookie `ds_user_id` otomatis dari `sessionid`.
- **Dukungan Full Cookie String**: Memungkinkan pengguna memasukkan string Cookie lengkap (`sessionid=...; ds_user_id=...; csrftoken=...`) secara langsung di Sidebar Web App.

### **v1.3.6** *(Penjelasan Masking Endpoint Logged-Out & Solusi Session Cookie)*
- **Penyebab Perbedaan Data**: Server Instagram secara sengaja menyembunyikan (*masking*) jumlah postingan asli (mengembalikan `Post: 0`) dan memblokir feed pada GraphQL endpoint `/api/v1/users/web_profile_info/` ketika diakses tanpa autentikasi cookie (*logged-out connection*).
- **Penguatan Cookie Binding**: Pada [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L50), `login_with_sessionid()` memperluas penyuntikan cookie ke domain `.instagram.com` dan `www.instagram.com` sehingga seluruh request mendapatkan sesi terautentikasi penuh.
- **Pelepasan Data Asli**: Dengan memasukkan `sessionid` di Sidebar, Instagram akan mengembalikan data asli lengkap (Username: `yayat.majalengka`, Nama: `Yayat Hidayatullah`, Kiriman: `124 kiriman`, Pengikut: `429`, Diikuti: `907`) dan mengunduh 124 postingan secara utuh.

### **v1.3.5** *(Pencegahan Delay Rate Limit 429 & Penanganan Retry Fast Response)*
- **Penambahan `max_connection_attempts=1`**: Pada [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L20), parameter `max_connection_attempts=1` dikonfigurasikan agar Instaloader tidak melakukan *wait/sleep* 10 menit ketika Instagram merespon `HTTP 429 - Too Many Requests` untuk koneksi anonim.
- **Pesan Edukasi IP Rate Limit**: Menampilkan penanganan exception dan pesan edukatif instan jika IP di-rate limit oleh Instagram, mengarahkan pengguna untuk menggunakan `sessionid` Cookie di Sidebar agar terbebas dari pembatasan IP anonim.

### **v1.3.4** *(Penataan Tampilan Detail Data Profil & Ekspor Metadata Mandiri)*
- **Penambahan Parameter `user_id`**: Modul [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L75) kini menyertakan `user_id` (Instagram Numeric ID) dalam dictionary hasil scraping profil.
- **Kartu & Tabel Metadata Profil Mandiri**: Pada [app.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/app.py#L185), seluruh atribut profil (Foto Profil, Username, Full Name, Bio, Link External, ID Akun, Followers, Following, Total Post, dan Status Privat/Publik) secara otomatis ditampilkan dalam **Kartu Ringkasan** & **Tabel Metadata Profil**.
- **Ekspor Data Profil Independen**: Menyediakan tombol khusus untuk mengunduh Metadata Profil ke format **CSV**, **JSON**, dan **Excel** secara mandiri (tetap berfungsi meskipun postingan bernilai 0 atau akun bersifat privat).

### **v1.3.3** *(Optimasi Akun dengan 0 Postingan & Respon Cepat)*
- **Penanganan Mediacount 0**: Menambahkan pemeriksaan awal pada `profile.mediacount`. Jika akun target bernilai `Post: 0` (seperti akun `@yayat.majalengka`), scraper pada [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L110) akan mencatat log `[INFO] Akun memili 0 postingan` dan langsung melewati iterator feed.
- **Respon Cepat di Streamlit**: UI di [app.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/app.py#L150) menampilkan informasi langsung `ℹ️ Akun @yayat.majalengka tidak memiliki postingan (0 Posts)` tanpa perlu menunggu *loading bar* yang menggantung.

### **v1.3.2** *(Penanganan Akun Privat & Feed Rate Limit Response)*
- **Penyebab Data Tidak Terambil**: Ketika melakukan scraping pada akun privat (seperti `@yayat.majalengka`) dalam *Mode Anonim*, Instagram membatasi pembacaan postingan feed, menyebabkan data postingan bernilai kosong `[]`.
- **Perbaikan pada `scraper.py`**:
  - Mengubah fungsi `scrape_profile_posts()` agar mengembalikan `[]` dengan log peringatan (*warning*) tanpa melemparkan error yang memadamkan aplikasi ketika mendeteksi akun privat.
- **Pesan Edukasi & Panduan di `app.py`**:
  - Menampilkan kartu informasi/peringatan khusus jika `0 postingan` berhasil diambil dari akun target:
    - *Akun Privat*: Menampilkan pesan edukatif bahwa akun bersifat **Privat** beserta panduan 4 langkah mudah untuk login menggunakan `sessionid` Cookie.
    - *Akun Tanpa Post*: Menampilkan informasi jika akun target belum memiliki postingan.
    - *Rate Limit Feed*: Memberikan instruksi penggunaan `sessionid` jika pembacaan feed dibatasi oleh Instagram.

### **v1.3.1** *(Fix Error: unsupported format string passed to NoneType.format)*
- **Penyebab Error**: Instagram GraphQL API terkadang mengembalikan nilai `None` untuk atribut `profile.followers`, `profile.mediacount`, `post.likes`, atau `post.comments` saat scraping profil publik tertentu atau saat *unauthenticated request*. Format string `{val:,}` pada Python melemparkan `TypeError: unsupported format string passed to NoneType.format` ketika memformat nilai `None`.
- **Perbaikan pada `scraper.py`**:
  - Menambahkan validasi nilai default `0` untuk atribut `userid`, `mediacount`, `followers`, `following`, `likes_count`, dan `comments_count` sebelum dikonversi dengan format angka berkoma (`,`).
- **Perbaikan pada `app.py`**:
  - Mengubah seluruh pemformatan metric Streamlit (`m1.metric`, `st.caption`, `st.write`) menjadi pembacaan aman: `(p.get('followers') or 0):,`.

### **v1.3.0** *(Backend Live Console & Detailed Logging System)*
- **Backend Logging Mechanism**: Menambahkan metode pencatatan log internal `_log()` dengan timestamp presisi milidetik dan level log (`[HTTP]`, `[INFO]`, `[DEBUG]`, `[SUCCESS]`, `[WARN]`, `[ERROR]`) pada [scraper.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/scraper.py#L40).
- **Streamlit Live Terminal Output**: Menambahkan tampilan terminal log berlatar gelap interaktif (`st.expander` + `st.code`) di [app.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/app.py#L140) untuk memantau aktivitas backend secara langsung:
  - Eksekusi request HTTP GET & GraphQL Instagram API.
  - Parsing node metadata profil, carousel sidecar, dan atribut postingan.
  - Log ukuran payload biner stream file saat mengunduh gambar/video.
- **Support Logging ZIP Bundling**: Mengalirkan log pengunduhan media real-time saat pembuatan file ZIP pada [exporter.py](file:///E:/ApplicationProject/PythonApp/ScrappingInstagram/exporter.py#L50).

### **v1.2.0** *(Tampilan Indikator & Status Proses Interaktif Real-Time)*
- **Interactive Step Tracker (`st.status`)**: Menggunakan komponen status kontainer Streamlit untuk menampilkan setiap tahapan proses scraping secara urut dan interaktif:
  - *Langkah 1*: Menghubungkan & verifikasi target (Profil / Hashtag / Media URL).
  - *Langkah 2*: Real-time progress bar (`st.progress`) & counter jumlah postingan terambil (`Current / Total`).
  - *Langkah 3*: Pengolahan data hasil scraping & render galeri media.
- **Progress Unduh ZIP Media**: Menambahkan indikator persentase real-time saat memaketkan dan mengunduh berkas gambar/video ke dalam arsip ZIP pada `exporter.py` dan `app.py`.
- **Notifikasi Toast System**: Menampilkan notifikasi kesuksesan pop-up (*toast*) ketika proses scraping dan pencarian media selesai.

### **v1.1.1** *(Non-Blocking Login Fallback & Graceful Error Handling)*
- **Perbaikan Fatal Error**: Mengubah mekanisme `InstagramScraper.__init__` agar tidak melemparkan *unhandled exception* ketika login password ditolak oleh Instagram.
- **Pesan Warning & Fallback Otomatis**: Jika login password atau sessionid gagal, status disimpan di `self.login_error` dan aplikasi secara otomatis beralih ke **Mode Anonim (Tanpa Login)** tanpa pernah memicu layar error merah di Streamlit.
- **Stabilitas UI**: Pengalaman pengguna (*UX*) menjadi jauh lebih mulus karena fitur scraping profil publik, hashtag, dan downloader media tetap 100% berfungsi meskipun akun Instagram pengguna memerlukan verifikasi 2FA/Checkpoint.

### **v1.1.0** *(Penanganan Autentikasi & Session Cookie Support)*
- **Perbaikan Issue Login**: Menangani error `Login error: "fail" status` dari Instagram akibat proteksi login otomatis (2FA/Checkpoint).
- **Fitur Baru (Session Cookie Login)**: Menambahkan dukungan login via **`sessionid` Cookie** browser pada `scraper.py` (`login_with_sessionid`) dan antarmuka `app.py`.
- **Dukungan Mode Akses**:
  1. *Mode Anonim (Tanpa Login)*: Default untuk scraping profil publik & hashtag tanpa perlu autentikasi.
  2. *Session Cookie (`sessionid`)*: Metode paling stabil & ampuh untuk menghindari blokir login Instagram.
  3. *Username & Password*: Dilengkapi pesan error informatif dan pengalihan otomatis (*fallback*) ke Mode Anonim tanpa memblokir aplikasi.
- **Pembaruan Panduan**: Menambahkan panduan langkah demi langkah cara mengambil `sessionid` dari Developer Tools browser di sidebar Streamlit.

### **v1.0.0** *(Initial Release)*
- Inisialisasi struktur proyek Web Scraping Instagram.
- Pembuatan modul `scraper.py` berbasis `instaloader`.
- Pembuatan modul `exporter.py` untuk ekspor CSV, JSON, Excel, dan ZIP packaging.
- Pembuatan antarmuka web Streamlit interaktif di `app.py`.
- Pembuatan dokumen `README.md` dan `APPS.md`.
