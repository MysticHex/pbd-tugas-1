"""
Bronze Layer Handler
Menyimpan data mentah tanpa modifikasi (immutable raw layer)
dengan indeks unik untuk mencegah duplikasi (deduplication).
"""
import logging
from typing import List, Dict, Any, Tuple
from pymongo.errors import BulkWriteError, DuplicateKeyError
from config.settings import (
    get_mongo_db,
    COLLECTION_BRONZE_YOUTUBE,
    COLLECTION_BRONZE_NEWS
)

logger = logging.getLogger(__name__)

def init_bronze_indexes():
    """Membuat indeks unik untuk mencegah duplikasi dokumen di Bronze Layer."""
    db = get_mongo_db()
    try:
        # Indeks unik untuk komentar YouTube berdasarkan comment_id
        db[COLLECTION_BRONZE_YOUTUBE].create_index("comment_id", unique=True)
        # Indeks unik untuk artikel berita berdasarkan URL
        db[COLLECTION_BRONZE_NEWS].create_index("url", unique=True)
        logger.info("Indeks unik Bronze Layer berhasil diinisialisasi.")
    except Exception as e:
        logger.warning(f"Catatan saat inisialisasi indeks Bronze: {e}")

def save_bronze_youtube(comments: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Menyimpan dokumen mentah komentar YouTube ke bronze_youtube.
    Mengembalikan (jumlah_disimpan_baru, jumlah_duplikat_dilewati).
    """
    if not comments:
        return 0, 0

    init_bronze_indexes()
    db = get_mongo_db()
    col = db[COLLECTION_BRONZE_YOUTUBE]

    inserted_count = 0
    duplicate_count = 0

    for doc in comments:
        comment_id = doc.get("comment_id")
        if not comment_id:
            continue
        try:
            res = col.update_one(
                {"comment_id": comment_id},
                {"$setOnInsert": doc},
                upsert=True
            )
            if res.upserted_id:
                inserted_count += 1
            else:
                duplicate_count += 1
        except DuplicateKeyError:
            duplicate_count += 1
        except Exception as e:
            logger.error(f"Gagal menyimpan komentar bronze {comment_id}: {e}")

    logger.info(f"Bronze YouTube: {inserted_count} baru disimpan, {duplicate_count} duplikat dilewati.")
    return inserted_count, duplicate_count

def save_bronze_news(news_list: List[Dict[str, Any]]) -> Tuple[int, int]:
    """
    Menyimpan dokumen mentah berita ke bronze_news.
    Mengembalikan (jumlah_disimpan_baru, jumlah_duplikat_dilewati).
    """
    if not news_list:
        return 0, 0

    init_bronze_indexes()
    db = get_mongo_db()
    col = db[COLLECTION_BRONZE_NEWS]

    inserted_count = 0
    duplicate_count = 0

    for doc in news_list:
        url = doc.get("url")
        if not url:
            continue
        try:
            res = col.update_one(
                {"url": url},
                {"$setOnInsert": doc},
                upsert=True
            )
            if res.upserted_id:
                inserted_count += 1
            else:
                duplicate_count += 1
        except DuplicateKeyError:
            duplicate_count += 1
        except Exception as e:
            logger.error(f"Gagal menyimpan berita bronze {url}: {e}")

    logger.info(f"Bronze News: {inserted_count} baru disimpan, {duplicate_count} duplikat dilewati.")
    return inserted_count, duplicate_count

def get_bronze_stats() -> Dict[str, int]:
    """Mengambil jumlah data terkini pada Bronze Layer."""
    db = get_mongo_db()
    yt_count = db[COLLECTION_BRONZE_YOUTUBE].count_documents({})
    news_count = db[COLLECTION_BRONZE_NEWS].count_documents({})
    return {
        "bronze_youtube": yt_count,
        "bronze_news": news_count,
        "total_bronze": yt_count + news_count
    }
