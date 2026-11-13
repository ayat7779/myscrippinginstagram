# 📸 Instagram Web Scraper & Media Downloader

Aplikasi Web interaktif modern berbasis Python **Streamlit** untuk scraping data profil Instagram, postingan, hashtag, pengunduh media (Foto, Video, Reels, Carousel), serta ekspor data ke **CSV**, **JSON**, **Excel**, dan **ZIP Bundle**.

---

## ✨ Fitur Utama

1. **👤 Scrape Profil & Postingan**:
   - Ekstraksi informasi profil lengkap: Foto profil, Bio, Jumlah Followers, Following, Jumlah Post, Status Verified & Private.
   - Ekstraksi postingan: Shortcode, Date/Timestamp, Type (Image/Video/Carousel), Likes Count, Comments Count, Caption, Hashtags, dan Media URLs.
2. **📥 Media & Reels Downloader**:
   - Pengunduhan media tunggal berdasarkan URL / Shortcode postingan atau Reels.
   - Preview gambar dan player video bawaan.
   - Unduh langsung file `.jpg` / `.mp4`.
3. **🏷️ Scrape Hashtag**:
   - Ekstraksi postingan publik berdasarkan Hashtag tertentu.
4. **📊 Ekspor Data & Bundle ZIP**:
   - Ekspor data hasil scraping ke format **CSV**, **JSON**, dan **Excel (.xlsx)**.
   - Fitur **Bundle Media (ZIP)** untuk mengunduh seluruh foto/video postingan sekaligus dalam 1 file ZIP.

---

## 🚀 Panduan Instalasi & Cara Menjalankan

### 1. Prasyarat
Pastikan Python versi **3.8+** sudah terinstall di komputer Anda.

### 2. Install Dependensi
Buka terminal / Command Prompt pada direktori project, lalu jalankan:

```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Web Streamlit
Jalankan perintah berikut di terminal:

```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser web lokal Anda (biasanya di `http://localhost:8501`).

---

## 📁 Struktur Project

```
ScrappingInstagram/
├── app.py              # Main Streamlit Web Application Interface
├── scraper.py          # Engine scraping Instagram (Instaloader wrapper)
├── exporter.py         # Utilitas ekspor data (CSV, JSON, Excel, ZIP)
├── requirements.txt    # Daftar dependensi Python
└── README.md           # Panduan dan dokumentasi aplikasi
```

---

## 💡 Tips Penggunaan & Batasan Rate Limit

- **Scraping Tanpa Login**: Sangat disarankan untuk profil publik dan batas postingan kecil (misalnya 10-20 post).
- **Login Akun Instagram (Opsional)**: Jika Anda ingin scraping jumlah postingan yang lebih banyak atau mengakses profil privat yang Anda ikuti, masukkan Username & Password akun Instagram di sidebar.
- **Rate Limit**: Instagram membatasi frekuensi permintaan. Gunakan jeda jika melakukan scraping secara beruntun.
