"""
Model Evaluation Module
Melakukan evaluasi menyeluruh terhadap performa model analisis sentimen:
Akurasi, Presisi, Recall, F1-Score, dan Confusion Matrix.
"""
import logging
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import cross_val_score

from sentiment.predict import get_model
from sentiment.train import load_training_dataset

logger = logging.getLogger(__name__)

def evaluate_model():
    """Mengevaluasi model pada dataset pelatihan dan validasi."""
    print("=" * 60)
    print("EVALUASI PERFORMA MODEL ANALISIS SENTIMEN")
    print("=" * 60)

    texts, labels = load_training_dataset()
    artifact = get_model()
    vectorizer = artifact["vectorizer"]
    classifier = artifact["classifier"]
    classes = artifact["classes"]

    X_vec = vectorizer.transform(texts)
    y_pred = classifier.predict(X_vec)

    acc = accuracy_score(labels, y_pred)
    report = classification_report(labels, y_pred, target_names=classes)
    cm = confusion_matrix(labels, y_pred, labels=classes)

    print(f"\nTotal Dataset Evaluasi : {len(texts)} sampel teks opini")
    print(f"Kelas Target            : {classes}")
    print(f"Akurasi Keseluruhan     : {acc * 100:.2f}%\n")
    print("-" * 60)
    print("LAPORAN KLASIFIKASI (PRECISION / RECALL / F1-SCORE):")
    print("-" * 60)
    print(report)

    print("-" * 60)
    print("CONFUSION MATRIX:")
    print("-" * 60)
    col_label = "Aktual \\ Pred"
    header = f"{col_label:<15}" + "".join([f"{c:<12}" for c in classes])
    print(header)
    print("-" * (15 + 12 * len(classes)))
    for i, actual_class in enumerate(classes):
        row = f"{actual_class:<15}" + "".join([f"{cm[i][j]:<12}" for j in range(len(classes))])
        print(row)
    print("=" * 60)

    return {
        "accuracy": acc,
        "classification_report": report,
        "confusion_matrix": cm,
        "classes": classes
    }

if __name__ == "__main__":
    evaluate_model()
