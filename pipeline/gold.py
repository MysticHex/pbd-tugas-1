"""
Gold / Analytics Layer Handler
Membaca data bersih dari Silver Layer (silver_comments),
menjalankan klasifikasi sentimen berbasis Machine Learning,
dan menyimpan hasil analitik siap pakai ke gold_sentiment.
"""
from collections import Counter
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Tuple

from config.settings import (
    get_mongo_db,
    COLLECTION_SILVER_COMMENTS,
    COLLECTION_GOLD_SENTIMENT
)
from sentiment.predict import predict_batch

logger = logging.getLogger(__name__)

def init_gold_indexes():
    """Membuat indeks pada Gold Layer untuk agregasi cepat dan dashboard."""
    db = get_mongo_db()
    try:
        db[COLLECTION_GOLD_SENTIMENT].create_index("comment_id", unique=True)
        db[COLLECTION_GOLD_SENTIMENT].create_index("sentiment")
        db[COLLECTION_GOLD_SENTIMENT].create_index("published_at")
        db[COLLECTION_GOLD_SENTIMENT].create_index("confidence")
        logger.info("Indeks Gold Layer berhasil diinisialisasi.")
    except Exception as e:
        logger.warning(f"Catatan inisialisasi indeks Gold: {e}")

def process_silver_to_gold(batch_size: int = 200) -> Tuple[int, int]:
    """
    Mengambil seluruh teks komentar dari silver_comments,
    melakukan inferensi sentimen & confidence score secara batch,
    dan menyimpan hasilnya ke gold_sentiment.
    Mengembalikan (jumlah_disimpan, jumlah_gagal).
    """
    init_gold_indexes()
    db = get_mongo_db()
    silver_col = db[COLLECTION_SILVER_COMMENTS]
    gold_col = db[COLLECTION_GOLD_SENTIMENT]

    cursor = list(silver_col.find({}))
    if not cursor:
        logger.info("Tidak ada data di silver_comments untuk diproses ke Gold Layer.")
        return 0, 0

    logger.info(f"Memproses {len(cursor)} komentar dari Silver ke Gold Layer...")

    texts_clean = [doc.get("text_clean", "") for doc in cursor]
    texts_raw = [doc.get("text_original", "") for doc in cursor]
    predictions = predict_batch(texts_clean, raw_texts=texts_raw, are_cleaned=True)

    saved_count = 0
    failed_count = 0

    for doc, pred in zip(cursor, predictions):
        comment_id = doc.get("comment_id")
        gold_doc = {
            "comment_id": comment_id,
            "source": doc.get("source", "youtube"),
            "video_id": doc.get("video_id", ""),
            "video_title": doc.get("video_title", ""),
            "author": doc.get("author", "Anonim"),
            "text_original": doc.get("text_original", ""),
            "text_clean": doc.get("text_clean", ""),
            "published_at": doc.get("published_at", ""),
            "like_count": int(doc.get("like_count", 0)),
            "sentiment": pred["sentiment"],
            "confidence": pred["confidence"],
            "probabilities": pred["probabilities"],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            gold_col.update_one(
                {"comment_id": comment_id},
                {"$set": gold_doc},
                upsert=True
            )
            saved_count += 1
        except Exception as e:
            logger.error(f"Gagal menyimpan analisis gold {comment_id}: {e}")
            failed_count += 1

    logger.info(f"Gold Layer: {saved_count} berhasil disimpan/diperbarui, {failed_count} gagal.")
    return saved_count, failed_count

def get_gold_analytics_summary() -> Dict[str, Any]:
    """Menghitung ringkasan KPI analitik dari gold_sentiment."""
    db = get_mongo_db()
    col = db[COLLECTION_GOLD_SENTIMENT]

    total_comments = col.count_documents({})
    positive_count = col.count_documents({"sentiment": "positive"})
    neutral_count = col.count_documents({"sentiment": "neutral"})
    negative_count = col.count_documents({"sentiment": "negative"})

    # Rata-rata confidence
    pipeline_conf = [
        {"$group": {"_id": None, "avg_conf": {"$avg": "$confidence"}}}
    ]
    conf_res = list(col.aggregate(pipeline_conf))
    avg_conf = conf_res[0]["avg_conf"] if conf_res else 0.0

    return {
        "total": total_comments,
        "positive": positive_count,
        "neutral": neutral_count,
        "negative": negative_count,
        "positive_pct": round((positive_count / total_comments * 100), 1) if total_comments > 0 else 0,
        "neutral_pct": round((neutral_count / total_comments * 100), 1) if total_comments > 0 else 0,
        "negative_pct": round((negative_count / total_comments * 100), 1) if total_comments > 0 else 0,
        "avg_confidence": round(avg_conf, 3)
    }

def get_top_keywords(limit: int = 20, sentiment_filter: str = None) -> List[Tuple[str, int]]:
    """Mengekstraksi frekuensi kata kunci teratas dari teks bersih."""
    db = get_mongo_db()
    query = {}
    if sentiment_filter and sentiment_filter != "all":
        query["sentiment"] = sentiment_filter

    cursor = db[COLLECTION_GOLD_SENTIMENT].find(query, {"text_clean": 1})
    words = []
    stopwords_ignore = {"yang", "dan", "di", "ke", "dari", "ini", "itu", "untuk", "pada", "adalah"}

    for doc in cursor:
        text = doc.get("text_clean", "")
        for w in text.split():
            if len(w) > 2 and w not in stopwords_ignore:
                words.append(w)

    counter = Counter(words)
    return counter.most_common(limit)
