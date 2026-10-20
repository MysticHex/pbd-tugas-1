"""
NLP Preprocessing Pipeline untuk Teks Opini Berbahasa Indonesia
Meliputi: Cleaning, Case folding, Slang Normalization, Stopword Removal, dan Stemming.
"""
import re
import json
import logging
from functools import lru_cache
from typing import Dict, List, Set

from config.settings import SLANG_DICT_PATH, STOPWORDS_PATH

logger = logging.getLogger(__name__)

# Cache kamus slang dan stopwords
_slang_dict: Dict[str, str] = {}
_stopwords_set: Set[str] = set()
_stemmer = None

# Kata negasi dan sentimen kritis yang TIDAK boleh dihapus oleh stopword removal
PRESERVED_NEGATIONS = {
    "tidak", "bukan", "belum", "tanpa", "jangan", "tak", "kurang", "batal", "tolak",
    "salah", "kecewa", "rusak", "bohong", "bodoh", "goblok", "anjing", "cacat",
    "gaib", "ghaib", "kotor", "buta", "prettt", "cemooh", "menyesal", "parah"
}

def load_slang_dict() -> Dict[str, str]:
    """Memuat kamus slang/singkatan media sosial."""
    global _slang_dict
    if not _slang_dict and SLANG_DICT_PATH.exists():
        try:
            with open(SLANG_DICT_PATH, "r", encoding="utf-8") as f:
                _slang_dict = json.load(f)
        except Exception as e:
            logger.error(f"Gagal memuat kamus slang: {e}")
    return _slang_dict

def load_stopwords() -> Set[str]:
    """Memuat daftar stopword bahasa Indonesia."""
    global _stopwords_set
    if not _stopwords_set and STOPWORDS_PATH.exists():
        try:
            with open(STOPWORDS_PATH, "r", encoding="utf-8") as f:
                words = [line.strip().lower() for line in f if line.strip()]
                _stopwords_set = set(w for w in words if w not in PRESERVED_NEGATIONS)
        except Exception as e:
            logger.error(f"Gagal memuat stopwords: {e}")
    return _stopwords_set

def get_stemmer():
    """Menginisialisasi Sastrawi Stemmer secara lazy."""
    global _stemmer
    if _stemmer is None:
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            factory = StemmerFactory()
            _stemmer = factory.create_stemmer()
        except Exception as e:
            logger.warning(f"Sastrawi stemmer tidak tersedia: {e}")
    return _stemmer

@lru_cache(maxsize=10000)
def stem_word(word: str) -> str:
    """Stem satu kata dengan memoization untuk efisiensi kecepatan."""
    stemmer = get_stemmer()
    if stemmer:
        return stemmer.stem(word)
    return word

def clean_regex(text: str) -> str:
    """Membersihkan URL, mention, hashtag, kata tersensor, dan karakter tidak perlu."""
    if not text or not isinstance(text, str):
        return ""
    
    # Pulihkan kata sensor bertanda bintang sebelum tanda baca dihapus
    text = re.sub(r"\bbod\*+h\b|\bb\*+doh\b", "bodoh", text, flags=re.IGNORECASE)
    text = re.sub(r"\banj\*+ng\b|\ba\*+jing\b", "anjing", text, flags=re.IGNORECASE)
    text = re.sub(r"\btol\*+l\b|\bt\*+lol\b", "tolol", text, flags=re.IGNORECASE)
    text = re.sub(r"\bgob\*+ok\b|\bg\*+blok\b", "goblok", text, flags=re.IGNORECASE)
    text = re.sub(r"\bb\*+go\b", "bego", text, flags=re.IGNORECASE)

    # Hapus URL
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    # Hapus mention (@user) dan hashtag (#tag)
    text = re.sub(r"[@#]\w+", " ", text)
    # Hapus email
    text = re.sub(r"\S+@\S+", " ", text)
    # Hapus karakter berulang lebih dari 2 kali (misal: "benerrrr" -> "benerr")
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    # Hapus simbol khusus dan angka, pertahankan alfabet dan spasi
    text = re.sub(r"[^a-zA-Z\s]", " ", text)
    # Case folding ke huruf kecil
    text = text.lower()
    # Rapikan whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def normalize_slang(text: str) -> str:
    """Mengganti kata slang/singkatan media sosial ke bentuk baku."""
    slang_map = load_slang_dict()
    if not slang_map:
        return text
    
    tokens = text.split()
    normalized_tokens = [slang_map.get(token, token) for token in tokens]
    return " ".join(normalized_tokens)

def remove_stopwords(text: str) -> str:
    """Menghapus stopword tanpa menghilangkan kata penentu sentimen."""
    stopwords = load_stopwords()
    if not stopwords:
        return text
    
    tokens = text.split()
    filtered_tokens = [token for token in tokens if token not in stopwords]
    return " ".join(filtered_tokens)

def apply_stemming(text: str) -> str:
    """Menerapkan stemming Sastrawi pada teks."""
    tokens = text.split()
    stemmed_tokens = [stem_word(token) for token in tokens]
    return " ".join(stemmed_tokens)

def preprocess_text(text: str, stem: bool = False) -> str:
    """
    Pipeline lengkap preprocessing teks:
    Raw -> Clean Regex -> Case Folding -> Slang Normalization -> Stopwords Removal (-> Stemming)
    """
    cleaned = clean_regex(text)
    normalized = normalize_slang(cleaned)
    no_stopwords = remove_stopwords(normalized)
    
    if stem and len(no_stopwords) > 0:
        return apply_stemming(no_stopwords)
    
    return no_stopwords
