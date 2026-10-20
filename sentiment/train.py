"""
Model Training Module untuk Analisis Sentimen Bahasa Indonesia
Menggunakan TF-IDF Vectorizer dan Calibrated Logistic Regression Classifier
untuk menghasilkan prediksi 3 kelas (positive, neutral, negative) serta confidence score.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from config.settings import TRAINING_SEED_PATH, MODEL_SAVE_PATH
from pipeline.preprocessing import preprocess_text

logger = logging.getLogger(__name__)

# Kata topik/entitas yang netral dan tidak boleh menjadi penentu sentimen positif/negatif
DOMAIN_TOPIC_WORDS = [
    "mk", "mahkamah", "konstitusi", "gibran", "ijazah", "presiden", "wapres", "slta", "sma"
]

def load_training_dataset() -> Tuple[list, list]:
    """Memuat dataset seed berlabel."""
    texts = []
    labels = []

    if TRAINING_SEED_PATH.exists():
        try:
            with open(TRAINING_SEED_PATH, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
                for item in seed_data:
                    clean = preprocess_text(item["text"])
                    if clean:
                        texts.append(clean)
                        labels.append(item["sentiment"])
        except Exception as e:
            logger.error(f"Gagal memuat dataset seed: {e}")

    return texts, labels

def train_sentiment_model() -> Dict[str, Any]:
    """
    Melatih model klasifikasi sentimen teks bahasa Indonesia
    dan menyimpannya ke disk (data/model_sentiment.pkl).
    """
    logger.info("Memulai pelatihan model analisis sentimen...")
    texts, labels = load_training_dataset()
    logger.info(f"Total dataset pelatihan: {len(texts)} sampel.")

    # Train / Test split untuk evaluasi
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )

    base_model = LogisticRegression(
        C=2.0,
        max_iter=1000,
        class_weight="balanced",
        random_state=42
    )

    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        min_df=1,
        sublinear_tf=True,
        stop_words=DOMAIN_TOPIC_WORDS
    )

    # Transform TF-IDF
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    # Calibrated Classifier
    calibrated_clf = CalibratedClassifierCV(estimator=base_model, cv=3)
    calibrated_clf.fit(X_train_vec, y_train)

    # Evaluasi pada data uji
    y_pred = calibrated_clf.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Fit ulang seluruh dataset untuk model produksi
    X_all_vec = vectorizer.fit_transform(texts)
    calibrated_clf.fit(X_all_vec, labels)

    # Simpan model & vectorizer
    MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    model_artifact = {
        "vectorizer": vectorizer,
        "classifier": calibrated_clf,
        "classes": [str(c) for c in calibrated_clf.classes_],
        "accuracy": acc
    }
    joblib.dump(model_artifact, MODEL_SAVE_PATH)
    logger.info(f"Model tersimpan di: {MODEL_SAVE_PATH}")

    return {
        "accuracy": acc,
        "report": report,
        "classes": [str(c) for c in calibrated_clf.classes_],
        "total_samples": len(texts)
    }

if __name__ == "__main__":
    result = train_sentiment_model()
    print("Hasil Pelatihan Model:")
    print(f"Akurasi: {result['accuracy'] * 100:.2f}%")
    print(f"Kelas: {result['classes']}")
