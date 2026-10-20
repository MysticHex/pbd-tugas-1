"""
Automated Crawler & Pipeline Scheduler (Nilai Tambah Priority 2)
Menjalankan proses pengambilan data dan pemrosesan secara periodik.
"""
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Pastikan root workspace terdaftar di sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import schedule

from collectors.youtube_api import collect_youtube_data
from collectors.news_scraper import collect_news_data
from pipeline.bronze import save_bronze_youtube, save_bronze_news, get_bronze_stats
from pipeline.silver import process_bronze_to_silver_comments, process_bronze_to_silver_news
from pipeline.gold import process_silver_to_gold, get_gold_analytics_summary

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [SCHEDULER-%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def run_scheduled_job():
    """Fungsi job yang dieksekusi secara berkala oleh scheduler."""
    logger.info("=" * 60)
    logger.info(f"MEMULAI SIKLUS PIPELINE TERJADWAL: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # 1. Data Collection & Bronze
        logger.info("[1/3] Mengambil data YouTube & Berita Scrapling...")
        comms = collect_youtube_data(count=30)
        news = collect_news_data(count=3)

        ins_yt, dup_yt = save_bronze_youtube(comms)
        ins_news, dup_news = save_bronze_news(news)
        logger.info(f"Bronze Update -> YouTube baru: {ins_yt}, Berita baru: {ins_news}")

        # 2. Silver Processing
        logger.info("[2/3] Memproses data Bronze ke Silver Layer...")
        proc_comms, _ = process_bronze_to_silver_comments()
        proc_news, _ = process_bronze_to_silver_news()
        logger.info(f"Silver Update -> Komentar bersih: {proc_comms}, Berita bersih: {proc_news}")

        # 3. Gold Sentiment Analysis
        logger.info("[3/3] Menjalankan Analisis Sentimen ke Gold Layer...")
        saved_gold, _ = process_silver_to_gold()
        logger.info(f"Gold Update -> Total analisis: {saved_gold}")

        summary = get_gold_analytics_summary()
        logger.info(f"Status Ringkasan: Total={summary['total']} | Positif={summary['positive']} | Netral={summary['neutral']} | Negatif={summary['negative']}")
        logger.info("Siklus terjadwal selesai dengan sukses.\n")

    except Exception as e:
        logger.error(f"Terjadi kesalahan pada siklus pipeline terjadwal: {e}", exc_info=True)

def start_scheduler(interval_minutes: int = 60):
    """Memulai scheduler dengan interval waktu yang ditentukan."""
    logger.info(f"Scheduler aktif! Pipeline akan berjalan setiap {interval_minutes} menit.")
    logger.info("Tekan Ctrl+C untuk menghentikan scheduler.")

    # Jalankan sekali di awal
    run_scheduled_job()

    # Jadwalkan berikutnya
    schedule.every(interval_minutes).minutes.do(run_scheduled_job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler dihentikan oleh pengguna.")

if __name__ == "__main__":
    interval = 60
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            pass
    start_scheduler(interval_minutes=interval)
