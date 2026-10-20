# Planning Project Big Data
## Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran

> **Basis tugas:** Tugas 1 Pengelolaan Big Data — MongoDB, minimal 2 sumber data, wajib API dan website, Bronze Layer, Silver Layer, serta live demo dari crawling sampai tahap akhir.

---

## 1. Tujuan Project

Membangun pipeline data end-to-end untuk mengumpulkan, menyimpan, mengolah, menganalisis, dan memvisualisasikan opini publik terhadap pemberitaan/putusan Mahkamah Konstitusi terkait isu ijazah Gibran.

Output utama:

1. Data hasil pengambilan dari API dan website.
2. Raw data tersimpan pada MongoDB Bronze Layer.
3. Data yang telah dibersihkan dan terstruktur tersimpan pada MongoDB Silver Layer.
4. Hasil sentiment analysis terhadap data opini publik.
5. Dashboard visualisasi hasil analisis.
6. Live demo dari proses crawling sampai dashboard.

---

# 2. Scope Project

### Topik

**Sentiment Analysis Opini Publik terhadap Putusan MK terkait Ijazah Gibran**

### Sumber Data

| Jenis | Sumber | Metode | Data Utama |
|---|---|---|---|
| API | YouTube Data API | API | Video & komentar |
| Website | Website berita resmi/media | Web Scraping | Artikel berita |

### Fokus Analisis

Fokus utama sentiment analysis adalah **komentar publik**, terutama komentar YouTube.

Data artikel berita digunakan sebagai data pendukung/konteks dan untuk memenuhi sumber website.

---

# 3. Arsitektur Pipeline

```text
                         DATA SOURCES
                              │
                ┌─────────────┴─────────────┐
                │                           │
          YouTube API                 News Website
                │                           │
                │                      Web Scraping
                │                           │
                └─────────────┬─────────────┘
                              ↓
                       DATA INGESTION
                              ↓
                    ┌──────────────────┐
                    │ MongoDB BRONZE   │
                    │    RAW DATA      │
                    └────────┬─────────┘
                             ↓
                       DATA PROCESSING
                             ↓
                  ┌─────────────────────┐
                  │ Cleaning            │
                  │ Normalization       │
                  │ Deduplication       │
                  │ NLP Preprocessing   │
                  └──────────┬──────────┘
                             ↓
                    ┌──────────────────┐
                    │ MongoDB SILVER   │
                    │ STRUCTURED DATA  │
                    └────────┬─────────┘
                             ↓
                     SENTIMENT ANALYSIS
                             ↓
                  ┌─────────────────────┐
                  │ Positive            │
                  │ Neutral             │
                  │ Negative            │
                  └──────────┬──────────┘
                             ↓
                       GOLD / ANALYTICS
                             ↓
                    ┌──────────────────┐
                    │    DASHBOARD     │
                    └──────────────────┘
```

---

# 4. Database Design

## 4.1 Bronze Layer

Raw data disimpan apa adanya sesuai hasil API/scraping.

### Collection

```text
bronze_youtube
bronze_news
```

### bronze_youtube

Contoh struktur:

```json
{
  "_id": "...",
  "source": "youtube",
  "video_id": "...",
  "comment_id": "...",
  "raw": {
    "text": "...",
    "author": "...",
    "published_at": "...",
    "like_count": 0
  },
  "scraped_at": "..."
}
```

### bronze_news

Contoh struktur:

```json
{
  "_id": "...",
  "source": "news",
  "raw": {
    "title": "...",
    "content": "...",
    "author": "...",
    "published_at": "...",
    "url": "..."
  },
  "scraped_at": "..."
}
```

**Prinsip:** jangan melakukan perubahan terhadap data asli pada Bronze.

---

# 5. Silver Layer

Silver berisi data yang sudah rapi dan siap dianalisis.

## 5.1 Collection

```text
silver_comments
silver_news
```

## 5.2 Preprocessing Komentar

```text
Raw Text
   ↓
Remove URL
   ↓
Remove Mention
   ↓
Remove Hashtag
   ↓
Remove Unnecessary Characters
   ↓
Lowercase
   ↓
Normalize Slang
   ↓
Remove Duplicate
   ↓
Tokenization
   ↓
Stopword Removal
   ↓
Stemming
```

## 5.3 Struktur silver_comments

```json
{
  "_id": "...",
  "source": "youtube",
  "video_id": "...",
  "comment_id": "...",
  "text_original": "...",
  "text_clean": "...",
  "published_at": "...",
  "like_count": 0,
  "language": "id"
}
```

---

# 6. Sentiment Analysis

Setelah Silver Layer selesai, data komentar diproses menggunakan model sentiment analysis.

## Output

```text
Positive
Neutral
Negative
```

### Pilihan model

#### Opsi utama untuk implementasi sederhana

```text
TF-IDF
   ↓
SVM / Logistic Regression
   ↓
Sentiment
```

#### Opsi pengembangan

```text
Indonesian Text
      ↓
IndoBERT
      ↓
Sentiment
```

Untuk pengerjaan dua minggu, prioritaskan model yang paling stabil dan mudah dievaluasi.

---

# 7. Gold / Analytics Layer

Gold Layer digunakan untuk menyimpan hasil analisis yang siap digunakan dashboard.

### Collection

```text
gold_sentiment
```

Contoh:

```json
{
  "comment_id": "...",
  "date": "2026-10-08",
  "source": "youtube",
  "sentiment": "negative",
  "confidence": 0.91
}
```

Jika topic analysis berhasil ditambahkan:

```json
{
  "comment_id": "...",
  "date": "2026-10-08",
  "source": "youtube",
  "topic": "putusan_mk",
  "sentiment": "negative",
  "confidence": 0.91
}
```

---

# 8. Dashboard Planning

## Dashboard Title

**Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran**

## Section 1 — KPI

```text
TOTAL DATA | POSITIVE | NEUTRAL | NEGATIVE
```

Tambahan:

```text
Total Video
Total Artikel
Last Updated
```

## Section 2 — Sentiment Distribution

Donut / bar chart:

```text
Positive
Neutral
Negative
```

## Section 3 — Sentiment Over Time

Line chart:

```text
Date/Time
    ↓
Sentiment Count
```

Tujuan:

- melihat perubahan volume opini;
- melihat dominasi sentiment;
- melihat perubahan setelah publikasi/pemberitaan.

## Section 4 — Sentiment by Source

Perbandingan:

```text
YouTube
Website
```

Catatan: jangan menyamakan artikel berita dengan opini publik. Sentiment publik utama berasal dari komentar.

## Section 5 — Top Keywords

```text
Keyword
Frequency
```

Contoh kategori:

```text
MK
ijazah
Gibran
putusan
hukum
politik
```

## Section 6 — Sample Comments

Tampilkan:

```text
Comment
Sentiment
Confidence
Like Count
Date
```

Filter:

```text
All
Positive
Neutral
Negative
```

---

# 9. Nilai Tambah

Berdasarkan ketentuan tugas, nilai tambah yang tersedia:

### Priority 1 — Docker Volume

MongoDB menggunakan volume terpisah agar data tidak hilang ketika container dihentikan/dihapus.

```text
Host Volume
     ↓
MongoDB Container
```

### Priority 2 — Crawling Otomatis

Menjalankan proses pengambilan data secara terjadwal.

```text
Scheduler
   ↓
API / Scraper
   ↓
MongoDB
```

Contoh:

```text
Setiap 1 jam
atau
Setiap 6 jam
```

### Priority 3 — Dashboard

Visualisasi hasil crawling dan sentiment analysis.

### Priority 4 — Search Engine

Jika waktu mencukupi:

```text
MongoDB
   ↓
Elasticsearch
   ↓
Fast Search
   ↓
Dashboard
```

### Tidak menjadi prioritas awal

- Real-time penuh
- Sharding
- Replica set kompleks

Kerjakan hanya jika pipeline utama sudah stabil.

---

# 10. Tech Stack

```text
Data Collection
├── YouTube Data API
└── Python Web Scraper

Database
└── MongoDB

Container
└── Docker + Docker Volume

Processing
├── Python
├── Pandas
└── NLP preprocessing

Machine Learning
├── Scikit-learn
└── TF-IDF + SVM / Logistic Regression

Visualization
└── Streamlit

Optional
└── Elasticsearch
```

---

# 11. Struktur Repository

```text
big-data-sentiment-mk/
│
├── README.md
├── docker-compose.yml
├── .env
├── requirements.txt
│
├── config/
│   └── config.py
│
├── collectors/
│   ├── youtube_api.py
│   └── news_scraper.py
│
├── pipeline/
│   ├── bronze.py
│   ├── preprocessing.py
│   ├── silver.py
│   └── gold.py
│
├── sentiment/
│   ├── train.py
│   ├── predict.py
│   └── evaluate.py
│
├── dashboard/
│   └── app.py
│
├── scheduler/
│   └── scheduler.py
│
├── data/
│   └── sample/
│
└── docs/
    ├── architecture.md
    └── demo-timeline.md
```

---

# 12. Planning Pengerjaan 2 Minggu

## Week 1 — Data Pipeline

### Day 1 — Setup

- [ ] Tentukan scope dan keyword
- [ ] Setup repository
- [ ] Setup Docker
- [ ] Setup MongoDB
- [ ] Setup Docker Volume
- [ ] Buat database dan collection

### Day 2 — YouTube API

- [ ] Setup API key
- [ ] Implement search video
- [ ] Implement pengambilan komentar
- [ ] Simpan raw data
- [ ] Test pagination
- [ ] Test duplicate handling

### Day 3 — Website Scraping

- [ ] Tentukan website
- [ ] Implement scraper
- [ ] Ambil judul
- [ ] Ambil isi artikel
- [ ] Ambil tanggal
- [ ] Ambil URL
- [ ] Simpan raw data

### Day 4 — Bronze Validation

- [ ] Validasi struktur document
- [ ] Pastikan raw data tidak berubah
- [ ] Test MongoDB persistence
- [ ] Buat query untuk melihat data Bronze

### Day 5 — Preprocessing

- [ ] Cleaning text
- [ ] Normalization
- [ ] Deduplication
- [ ] Language filtering
- [ ] Tokenization
- [ ] Stopword removal
- [ ] Stemming

### Day 6 — Silver Layer

- [ ] Buat `silver_comments`
- [ ] Buat `silver_news`
- [ ] Masukkan hasil preprocessing
- [ ] Validasi data
- [ ] Buat aggregation dasar

### Day 7 — Integration Test

- [ ] API → Bronze → Silver
- [ ] Website → Bronze → Silver
- [ ] Pastikan pipeline dapat dijalankan ulang
- [ ] Dokumentasikan hasil Week 1

---

# 13. Week 2 — Analytics & Dashboard

## Day 8 — Dataset Sentiment

- [ ] Tentukan metode labeling
- [ ] Siapkan dataset training/evaluation
- [ ] Split train/test
- [ ] TF-IDF
- [ ] Train model

## Day 9 — Model Evaluation

- [ ] Accuracy
- [ ] Precision
- [ ] Recall
- [ ] F1-score
- [ ] Confusion matrix
- [ ] Simpan model

## Day 10 — Sentiment Pipeline

- [ ] Jalankan model terhadap Silver
- [ ] Generate sentiment
- [ ] Generate confidence
- [ ] Simpan hasil ke Gold
- [ ] Validasi hasil

## Day 11 — Dashboard

- [ ] Layout dashboard
- [ ] KPI
- [ ] Sentiment distribution
- [ ] Timeline
- [ ] Source comparison
- [ ] Keyword analysis
- [ ] Comment explorer

## Day 12 — Automated Crawling

- [ ] Buat scheduler
- [ ] Test crawling otomatis
- [ ] Test penyimpanan incremental
- [ ] Test duplicate handling
- [ ] Update dashboard

## Day 13 — Optional Value Added

Prioritas:

- [ ] Elasticsearch
- [ ] Search komentar
- [ ] Index data

Jika tidak sempat:

> Skip Elasticsearch dan fokus pada stabilitas pipeline.

## Day 14 — Final Demo

- [ ] Bersihkan repository
- [ ] Pastikan `.env` tidak ikut commit
- [ ] Test Docker dari awal
- [ ] Test crawling
- [ ] Test MongoDB
- [ ] Test preprocessing
- [ ] Test sentiment
- [ ] Test dashboard
- [ ] Rekam live demo
- [ ] Upload video ke YouTube sebagai unlisted
- [ ] Buat `.txt` submission
- [ ] Tambahkan timestamp capaian pada deskripsi video

---

# 14. Skenario Live Demo

Urutan demo harus mengikuti aliran data:

```text
01. Start Docker
        ↓
02. MongoDB Running
        ↓
03. Run YouTube API
        ↓
04. Run Website Scraper
        ↓
05. Show Bronze Collection
        ↓
06. Run Data Processing
        ↓
07. Show Silver Collection
        ↓
08. Run Sentiment Analysis
        ↓
09. Show Sentiment Result
        ↓
10. Open Dashboard
        ↓
11. Filter Sentiment
        ↓
12. Show Timeline / Statistics
        ↓
13. Demonstrate Search (optional)
```

---

# 15. Target Output

Pada akhir project harus tersedia:

```text
[✓] MongoDB Container
[✓] Docker Volume
[✓] API Data Source
[✓] Website Data Source
[✓] Crawling
[✓] Bronze Layer
[✓] Data Processing
[✓] Silver Layer
[✓] Sentiment Analysis
[✓] Dashboard
[✓] Live Demo
```

Optional:

```text
[ ] Automated Crawling
[ ] Elasticsearch
[ ] Real-time
[ ] Distributed MongoDB
```

---

# 16. Prioritas Pengerjaan

Gunakan prioritas berikut agar project tidak over-engineered.

### P0 — Wajib selesai

```text
MongoDB
API
Website
Bronze
Silver
Sentiment
Dashboard
Live Demo
```

### P1 — Nilai tambah yang realistis

```text
Docker Volume
Automated Crawling
```

### P2 — Jika masih ada waktu

```text
Elasticsearch
Search
```

### P3 — Jangan dikerjakan sebelum semuanya stabil

```text
Real-time
Sharding
Replica
```

---

# 17. Definition of Done

Project dianggap selesai apabila:

- [ ] Data dapat diambil dari API.
- [ ] Data dapat diambil dari website.
- [ ] Raw data masuk MongoDB Bronze.
- [ ] Data Bronze dapat dipertahankan menggunakan Docker Volume.
- [ ] Data dapat diproses menjadi data terstruktur.
- [ ] Data hasil processing masuk MongoDB Silver.
- [ ] Sentiment analysis dapat dijalankan.
- [ ] Hasil sentiment dapat disimpan.
- [ ] Dashboard dapat membaca data MongoDB.
- [ ] Dashboard menampilkan hasil analisis.
- [ ] Pipeline dapat dijalankan dari awal.
- [ ] Live demo memperlihatkan crawling sampai dashboard.

---

# 18. Catatan Penting

Project ini bukan hanya membuat dashboard sentiment.

Nilai utama project adalah:

```text
DATA COLLECTION
       +
NOSQL STORAGE
       +
DATA PROCESSING
       +
SENTIMENT ANALYSIS
       +
DATA VISUALIZATION
```

Sehingga saat presentasi, jangan hanya menunjukkan dashboard. Tunjukkan bagaimana data bergerak dari:

**API/Website → Bronze → Silver → Sentiment → Dashboard.**

**Menggunakan wsl untuk docker nya**