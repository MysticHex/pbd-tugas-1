"""
Master CLI Orchestrator & Live Demo Runner
Pipeline Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran
Tugas 1 Pengelolaan Big Data
"""
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Setup path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Force UTF-8 encoding on Windows console if supported
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config.settings import (
    check_mongo_connection,
    resolve_mongo_uri,
    get_mongo_db,
    COLLECTION_BRONZE_YOUTUBE,
    COLLECTION_BRONZE_NEWS,
    COLLECTION_SILVER_COMMENTS,
    COLLECTION_SILVER_NEWS,
    COLLECTION_GOLD_SENTIMENT,
    YOUTUBE_API_KEY
)
from collectors.youtube_api import collect_youtube_data
from collectors.news_scraper import collect_news_data
from pipeline.bronze import save_bronze_youtube, save_bronze_news, get_bronze_stats
from pipeline.silver import process_bronze_to_silver_comments, process_bronze_to_silver_news, get_silver_stats
from pipeline.gold import process_silver_to_gold, get_gold_analytics_summary
from sentiment.train import train_sentiment_model
from sentiment.evaluate import evaluate_model

BANNER = r"""
========================================================================
     BIG DATA PIPELINE: ANALISIS SENTIMEN PUTUSAN MK IJAZAH GIBRAN     
       MongoDB (WSL Docker Volume) | Scrapling | Streamlit Dashboard    
========================================================================
"""

def print_step_header(step_num: int, title: str):
    print("\n" + "=" * 72)
    print(f" [LANGKAH {step_num}] {title.upper()}")
    print("=" * 72)

def step_check_env():
    print_step_header(1, "Verifikasi Lingkungan Sistem & Koneksi MongoDB (WSL)")
    uri = resolve_mongo_uri()
    print(f"[*] Target URI MongoDB : {uri}")
    
    is_conn = check_mongo_connection()
    if is_conn:
        print("[OK] Status MongoDB     : TERHUBUNG (OK)")
        db = get_mongo_db()
        print(f"[OK] Database           : '{db.name}'")
        
        # Cek statistik dokumen saat ini
        b_stats = get_bronze_stats()
        s_stats = get_silver_stats()
        g_stats = get_gold_analytics_summary()
        
        print("\n[*] Ringkasan Data Saat Ini:")
        print(f"    - Bronze YouTube   : {b_stats['bronze_youtube']} dokumen")
        print(f"    - Bronze Berita    : {b_stats['bronze_news']} dokumen")
        print(f"    - Silver Komentar  : {s_stats['silver_comments']} dokumen")
        print(f"    - Silver Berita    : {s_stats['silver_news']} dokumen")
        print(f"    - Gold Sentimen    : {g_stats['total']} dokumen")
    else:
        print("[FAIL] Status MongoDB   : GAGAL TERHUBUNG!")
        print("       Silakan pastikan container Docker aktif di WSL:")
        print("       wsl -d Ubuntu docker compose up -d")
        return False

    if YOUTUBE_API_KEY:
        print("[OK] YouTube API Key    : TERDETEKSI")
    else:
        print("[INFO] YouTube API Key  : Tidak ada di .env (Fallback Mock Ingestor aktif)")

    return True

def step_crawl(limit_yt: int = 40, limit_news: int = 3, video_urls: list = None):
    print_step_header(2, "Data Collection & Bronze Ingestion (Raw Layer)")
    if video_urls:
        print(f"[*] Mengambil komentar dari video spesifik: {video_urls}...")
        yt_comments = collect_youtube_data(video_ids=video_urls)
    else:
        print(f"[*] Mengambil komentar YouTube via search query (target: {limit_yt})...")
        yt_comments = collect_youtube_data(count=limit_yt)
    ins_yt, dup_yt = save_bronze_youtube(yt_comments)
    print(f"[OK] Bronze YouTube: {ins_yt} baru disimpan, {dup_yt} duplikat diabaikan.")

    print(f"\n[*] Mengambil artikel berita dengan Scrapling (target: {limit_news})...")
    news_articles = collect_news_data(count=limit_news)
    ins_news, dup_news = save_bronze_news(news_articles)
    print(f"[OK] Bronze News: {ins_news} baru disimpan, {dup_news} duplikat diabaikan.")

    stats = get_bronze_stats()
    print(f"\n[OK] Total Dokumen Bronze Layer: {stats['total_bronze']}")

def step_process():
    print_step_header(3, "NLP Preprocessing & Silver Transformation (Clean Layer)")
    print("[*] Membersihkan komentar YouTube (Regex, Slang Normalizer, Stopwords)...")
    proc_c, skip_c = process_bronze_to_silver_comments()
    print(f"[OK] Silver Komentar: {proc_c} berhasil dibersihkan & distrukturkan ({skip_c} dilewati).")

    print("\n[*] Menstrukturkan artikel berita ke Silver Layer...")
    proc_n, skip_n = process_bronze_to_silver_news()
    print(f"[OK] Silver Berita: {proc_n} artikel diproses ({skip_n} dilewati).")

    stats = get_silver_stats()
    print(f"\n[OK] Total Dokumen Silver Layer: {stats['total_silver']}")

def step_train():
    print_step_header(4, "Pelatihan & Evaluasi Model Analisis Sentimen")
    train_res = train_sentiment_model()
    print(f"[OK] Akurasi Pelatihan : {train_res['accuracy'] * 100:.2f}%")
    print(f"[OK] Kelas Sentimen    : {train_res['classes']}")
    print("\n[*] Evaluasi Detail Model:")
    evaluate_model()

def step_analyze():
    print_step_header(5, "Analisis Sentimen & Gold Layer Ingestion")
    print("[*] Menjalankan inferensi Machine Learning pada data Silver Komentar...")
    saved_gold, failed_gold = process_silver_to_gold()
    print(f"[OK] Gold Sentimen: {saved_gold} analisis tersimpan ({failed_gold} gagal).")

    summary = get_gold_analytics_summary()
    print("\n" + "-" * 50)
    print("HASIL ANALISIS SENTIMEN PUBLIK TERAKHIR:")
    print("-" * 50)
    print(f" Total Komentar : {summary['total']}")
    print(f" Positif        : {summary['positive']} ({summary['positive_pct']}%)")
    print(f" Netral         : {summary['neutral']} ({summary['neutral_pct']}%)")
    print(f" Negatif        : {summary['negative']} ({summary['negative_pct']}%)")
    print(f" Rata-rata Skor : {summary['avg_confidence']}")
    print("-" * 50)

def step_dashboard():
    print_step_header(6, "Menjalankan Streamlit Dashboard")
    dashboard_path = BASE_DIR / "dashboard" / "app.py"
    print(f"[*] Menjalankan command: streamlit run {dashboard_path}")
    print("[*] Dashboard dapat diakses di http://localhost:8501")
    subprocess.run(["streamlit", "run", str(dashboard_path)])

def interactive_menu():
    print(BANNER)
    while True:
        print("\nPILIHAN MENU DEMO PIPELINE:")
        print("  1. Cek Lingkungan & Koneksi MongoDB (WSL Docker)")
        print("  2. Crawl Data (YouTube API + Scrapling) -> Bronze Layer")
        print("  3. Preprocessing NLP -> Silver Layer")
        print("  4. Latih & Evaluasi Model Sentimen")
        print("  5. Jalankan Analisis Sentimen -> Gold Layer")
        print("  6. Buka Streamlit Dashboard")
        print("  7. Jalankan Seluruh Pipeline End-to-End (1 -> 2 -> 3 -> 5 -> 6)")
        print("  0. Keluar")
        
        choice = input("\nPilih menu [0-7]: ").strip()
        if choice == "1":
            step_check_env()
        elif choice == "2":
            step_crawl()
        elif choice == "3":
            step_process()
        elif choice == "4":
            step_train()
        elif choice == "5":
            step_analyze()
        elif choice == "6":
            step_dashboard()
        elif choice == "7":
            if step_check_env():
                step_crawl()
                step_process()
                step_train()
                step_analyze()
                step_dashboard()
        elif choice == "0":
            print("Keluar dari program. Terima kasih!")
            break
        else:
            print("Pilihan tidak valid, silakan coba lagi.")

def main():
    parser = argparse.ArgumentParser(description="Big Data Sentiment Analysis Pipeline Runner")
    parser.add_argument(
        "--step",
        choices=["check-env", "crawl", "process", "train", "analyze", "dashboard", "all"],
        help="Langkah pipeline yang ingin dieksekusi langsung"
    )
    parser.add_argument("--limit-yt", type=int, default=40, help="Jumlah komentar YouTube")
    parser.add_argument("--limit-news", type=int, default=3, help="Jumlah artikel berita")
    parser.add_argument("--video-urls", nargs="+", help="Daftar URL atau ID video YouTube spesifik")
    parser.add_argument("--no-dashboard", action="store_true", help="Jangan buka dashboard saat --step all")

    args = parser.parse_args()

    if not args.step:
        interactive_menu()
        return

    print(BANNER)
    if args.step == "check-env":
        step_check_env()
    elif args.step == "crawl":
        step_crawl(limit_yt=args.limit_yt, limit_news=args.limit_news, video_urls=args.video_urls)
    elif args.step == "process":
        step_process()
    elif args.step == "train":
        step_train()
    elif args.step == "analyze":
        step_analyze()
    elif args.step == "dashboard":
        step_dashboard()
    elif args.step == "all":
        if step_check_env():
            step_crawl(limit_yt=args.limit_yt, limit_news=args.limit_news, video_urls=args.video_urls)
            step_process()
            step_train()
            step_analyze()
            if not args.no_dashboard:
                step_dashboard()

if __name__ == "__main__":
    main()
