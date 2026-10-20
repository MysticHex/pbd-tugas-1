# Panduan Lengkap Skenario Live Demo Ujian

Gunakan panduan ini sebagai urutan presentasi saat mendemonstrasikan tugas di hadapan dosen/penilai.  
Alur demonstrasi dirancang mengikuti pergerakan data dari **Sumber → Bronze → Silver → Gold → Dashboard**.

---

## Ringkasan Alur Demo (10-15 Menit)

| No | Tahapan | Aksi / Perintah | Hal yang Ditunjukkan ke Penilai |
|---|---|---|---|
| 1 | **Cek Infrastruktur Docker WSL** | `wsl -d Ubuntu docker compose ps` | Container `pbd_mongodb` dan `pbd_mongo_express` aktif dengan named volume `pbd_mongo_data`. |
| 2 | **Buka Database Web GUI** | Browser: `http://localhost:8081` | Tunjukkan Mongo Express dan database `bigdata_sentiment_mk`. |
| 3 | **Crawl Data (API & Scrapling)** | `python main.py --step crawl` | Pengambilan komentar dari YouTube API dan artikel berita menggunakan Scrapling. |
| 4 | **Periksa Bronze Layer** | Browser Mongo Express: Refresh | Tunjukkan koleksi `bronze_youtube` dan `bronze_news` (data asli mentah tanpa diubah). |
| 5 | **Jalankan Preprocessing** | `python main.py --step process` | Cleaning regex, kamus slang bahasa Indonesia, stopword removal, dan strukturisasi. |
| 6 | **Periksa Silver Layer** | Browser Mongo Express: Refresh | Tunjukkan `silver_comments` (`text_clean`) dan `silver_news`. |
| 7 | **Latih / Evaluasi Model ML** | `python main.py --step train` | Model TF-IDF + Calibrated Classifier, akurasi, dan confusion matrix. |
| 8 | **Jalankan Sentimen ke Gold** | `python main.py --step analyze` | Prediksi sentimen 3 kelas (positif, netral, negatif) beserta confidence score. |
| 9 | **Periksa Gold Layer** | Browser Mongo Express: Refresh | Tunjukkan dokumen di `gold_sentiment`. |
| 10 | **Buka & Jelajahi Dashboard** | `python main.py --step dashboard` (Browser `http://localhost:8501`) | KPI cards, Donut Chart, Tren Timeline, Word Frequency, Comment Explorer dengan filter. |
| 11 | **Buktikan Nilai Tambah (Volume)** | Restart container di WSL lalu cek data tetap utuh. | Bukti bahwa data tidak hilang saat container restart. |

---

## Langkah Detail & Skrip Penjelasan

### Langkah 1 — Menunjukkan Infrastruktur Docker di WSL
Buka terminal dan jalankan:
```powershell
wsl -d Ubuntu docker compose ps
```
> **Penjelasan ke Dosen:**  
> *"Sistem menggunakan MongoDB 7.0 yang dijalankan dalam container Docker di WSL2 dengan named volume `pbd_mongo_data`. Kami juga menyertakan Mongo Express di port 8081 untuk visualisasi database."*

---

### Langkah 2 — Menjalankan Crawling Data (Bronze Layer)
Jalankan perintah:
```powershell
python main.py --step crawl
```
> **Penjelasan ke Dosen:**  
> *"Pada tahap ini, kami mengumpulkan data dari dua sumber wajib: (1) YouTube Data API v3 untuk opini publik/komentar dan (2) Web Scraping portal berita menggunakan library modern Scrapling. Data langsung disimpan apa adanya ke Bronze Layer (`bronze_youtube` dan `bronze_news`) dengan indeks pencegah duplikasi."*

Buka `http://localhost:8081` dan tunjukkan isi dokumen di `bronze_youtube`.

---

### Langkah 3 — Pembersihan Teks (Silver Layer)
Jalankan perintah:
```powershell
python main.py --step process
```
> **Penjelasan ke Dosen:**  
> *"Pada tahap pemrosesan data, komentar mentah dibersihkan menggunakan pipeline NLP Bahasa Indonesia: penghapusan URL, mention, emoji, konversi singkatan/slang media sosial menggunakan kamus normalisasi, dan stopword removal dengan tetap mempertahankan kata negasi seperti 'tidak' dan 'belum'. Hasilnya disimpan ke Silver Layer."*

Buka Mongo Express dan tunjukkan perbandingan kolom `text_original` dengan `text_clean` di `silver_comments`.

---

### Langkah 4 — Evaluasi Model Sentimen & Eksekusi Gold Layer
Jalankan evaluasi model:
```powershell
python main.py --step train
```
Lalu jalankan inferensi sentimen ke Gold Layer:
```powershell
python main.py --step analyze
```
> **Penjelasan ke Dosen:**  
> *"Kami menggunakan model Machine Learning TF-IDF dengan Calibrated Logistic Regression untuk mengklasifikasikan komentar ke dalam kelas Positif, Netral, dan Negatif. Model menghasilkan confidence score untuk mengukur tingkat keyakinan prediksi. Data analitik disimpan pada Gold Layer (`gold_sentiment`)."*

---

### Langkah 5 — Demonstrasi Dashboard Streamlit
Jalankan dashboard:
```powershell
python main.py --step dashboard
```
Browser akan otomatis membuka `http://localhost:8501`.  
**Fitur yang perlu ditunjukkan di dashboard:**
1. **KPI Cards**: Total data terkumpul, rasio sentimen positif, netral, dan negatif.
2. **Donut Chart**: Distribusi proporsi opini publik.
3. **Timeline Line Chart**: Dinamika volume sentimen dari hari ke hari.
4. **Frekuensi Kata Kunci**: Kata kunci yang paling sering muncul (misal: *ijazah, sah, putusan, adil, hakim*).
5. **Comment Explorer**: Uji coba filter sentimen (pilih Positif, Netral, atau Negatif) dan slider *minimum confidence*.
6. **Tombol Live Pipeline di Sidebar**: Tunjukkan bahwa penguji dapat mengeklik tombol "Jalankan Full Pipeline" untuk memperbarui data langsung dari UI.

---

### Langkah 6 — Pembuktian Persistensi Docker Volume (Nilai Tambah)
Untuk membuktikan data tidak hilang saat container dimatikan:
```powershell
wsl -d Ubuntu docker compose down
wsl -d Ubuntu docker compose up -d
python main.py --step check-env
```
Tunjukkan bahwa jumlah dokumen di Bronze, Silver, dan Gold tetap utuh 100%.
