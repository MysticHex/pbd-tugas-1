# Big Data Pipeline: Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran

Tugas 1 Mata Kuliah Pengelolaan Big Data  
Teknologi: **MongoDB (WSL Docker Volume)** | **YouTube Data API v3** | **Scrapling Web Scraper** | **Scikit-Learn** | **Streamlit**

---

## 🎯 Ringkasan Proyek

Proyek ini membangun pipeline data *end-to-end* berskala Big Data untuk mengumpulkan, menyimpan, memproses, menganalisis sentimen, dan memvisualisasikan opini publik terkait putusan Mahkamah Konstitusi (MK) mengenai isu ijazah Gibran Rakabuming Raka.

Arsitektur data mengadopsi prinsip **Medallion Data Lakehouse**:
- **Bronze Layer**: Penyimpanan data mentah (*raw data*) langsung dari YouTube Data API v3 dan Web Scraper Scrapling secara *immutable*.
- **Silver Layer**: Data yang telah dibersihkan melalui pipeline NLP Bahasa Indonesia (regex, kamus normalisasi slang media sosial, stopword removal, dan stemming).
- **Gold Layer**: Data hasil inferensi model Machine Learning klasifikasi sentimen 3 kelas (Positif, Netral, Negatif) dilengkapi *confidence score*.
- **Visualisasi**: Dashboard interaktif berbasis Streamlit lengkap dengan KPI, visualisasi distribusi donat, timeline sentimen, analisis kata kunci, dan penjelajah komentar.

---

## ⚙️ Persyaratan Sistem & Instalasi

### 1. Prasyarat
- Python 3.10+ (Teruji pada Python 3.13)
- Docker & WSL2 (Ubuntu)

### 2. Instalasi Dependensi Python
```powershell
pip install -r requirements.txt
```

### 3. Konfigurasi Environment (`.env`)
Salin file `.env.example` ke `.env`:
```powershell
copy .env.example .env
```
Isi `YOUTUBE_API_KEY` jika Anda memiliki API Key Google Cloud. Jika dikosongkan, sistem otomatis mengaktifkan *realistic mock collector* sehingga demo tetap berjalan tanpa kendala.

### 4. Menjalankan Seluruh Project di Docker (MongoDB, Mongo Express, Streamlit Dashboard)
Jalankan seluruh stack container menggunakan Docker Compose (via WSL atau Docker Desktop):
```powershell
# Jalankan seluruh service (Database, Web GUI, & Streamlit Dashboard)
wsl -d Ubuntu docker compose up -d
```
Verifikasi Akses Layanan:
- **Streamlit Web Dashboard**: [http://localhost:8501](http://localhost:8501)
- **Mongo Express GUI**: [http://localhost:8081](http://localhost:8081)
- **MongoDB Database**: Port `27017`

> *Catatan: Anda juga dapat menjalankan perintah pipeline langsung di dalam container:*
> ```powershell
> wsl -d Ubuntu docker compose exec dashboard python main.py --step all
> ```

---

## 🚀 Menjalankan Pipeline & Live Demo

Jalankan script orchestrator [main.py](file:///d:/pbd/main.py):

### Opsi 1: Menu Interaktif
```powershell
python main.py
```

### Opsi 2: Eksekusi Langkah Tertentu
```powershell
# 1. Periksa koneksi lingkungan dan MongoDB
python main.py --step check-env

# 2. Ambil data mentah (YouTube API & Scrapling) -> Bronze Layer
python main.py --step crawl

# 3. Proses pembersihan data NLP -> Silver Layer
python main.py --step process

# 4. Latih dan evaluasi model sentimen
python main.py --step train

# 5. Jalankan inferensi sentimen -> Gold Layer
python main.py --step analyze

# 6. Buka Dashboard Streamlit
python main.py --step dashboard
```

### Opsi 3: Eksekusi Seluruh Pipeline Otomatis Sekaligus
```powershell
python main.py --step all
```

---

## 🕒 Otomasi Crawling Terjadwal (Nilai Tambah P2)

Untuk menjalankan crawling dan pemrosesan otomatis secara periodik di background:
```powershell
python scheduler/scheduler.py 60
```
*(Parameter `60` menandakan interval dalam menit).*

---

## 📁 Struktur Direktori

```text
d:\pbd/
├── docker-compose.yml              # Konfigurasi MongoDB + Mongo Express + Named Volume
├── .env.example                    # Template variabel konfigurasi
├── .env                            # Variabel environment lokal
├── requirements.txt                # Dependensi Python
├── main.py                         # Master CLI orchestrator & runner demo
│
├── config/                         # Pengaturan koneksi MongoDB & auto-discovery WSL
│   ├── __init__.py
│   └── settings.py
│
├── collectors/                     # Modul pengumpul data (API & Scrapling)
│   ├── __init__.py
│   ├── youtube_api.py
│   ├── news_scraper.py
│   └── mock_data.py
│
├── pipeline/                       # Pengelola Medallion Architecture (Bronze, Silver, Gold)
│   ├── __init__.py
│   ├── bronze.py
│   ├── preprocessing.py
│   ├── silver.py
│   └── gold.py
│
├── sentiment/                      # Model Machine Learning Analisis Sentimen
│   ├── __init__.py
│   ├── train.py
│   ├── predict.py
│   └── evaluate.py
│
├── dashboard/                      # Aplikasi visualisasi data interaktif Streamlit
│   ├── __init__.py
│   └── app.py
│
├── scheduler/                      # Penjadwalan crawling berkala (Priority 2)
│   ├── __init__.py
│   └── scheduler.py
│
├── data/                           # Kamus bahasa & dataset model
│   ├── slang_dictionary.json
│   ├── stopwords_id.txt
│   ├── training_seed.json
│   └── model_sentiment.pkl
│
└── docs/                           # Dokumentasi teknis & panduan demo
    ├── architecture.md
    └── live_demo_guide.md
```

---

## 📚 Panduan Demonstrasi Ujian

Buka [docs/live_demo_guide.md](file:///d:/pbd/docs/live_demo_guide.md) untuk panduan urutan presentasi dan poin-poin penjelasan di hadapan dosen penguji.
