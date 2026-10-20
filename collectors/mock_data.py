"""
Modul sample mock data generator untuk simulasi pengujian dan fallback
apabila YouTube API key belum dikonfigurasi atau kuota API tercapai.
"""
from datetime import datetime, timezone
import random
import uuid

SAMPLE_NEWS_ARTICLES = [
    {
        "url": "https://nasional.kompas.com/read/2024/04/22/putusan-mk-tolak-gugatan-sengketa-ijazah-dan-syarat-pencalonan",
        "title": "Mahkamah Konstitusi Tolak Seluruh Gugatan Terkait Persyaratan dan Ijazah Calon",
        "author": "Tim Redaksi Nasional",
        "published_at": "2024-04-22T14:30:00Z",
        "content": "Jakarta, Mahkamah Konstitusi (MK) resmi menolak seluruh gugatan sengketa hasil pemilihan umum yang mempermasalahkan keabsahan dokumen persyaratan pencalonan wakil presiden Gibran Rakabuming Raka. Dalam amar putusannya, majelis hakim konstitusi menegaskan bahwa proses verifikasi berkas oleh KPU telah sesuai regulasi perundang-undangan dan tidak ditemukan bukti pemalsuan dokumen sah."
    },
    {
        "url": "https://news.detik.com/berita/d-7301234/pertimbangan-hakim-mk-soal-isu-ijazah-gibran-tidak-berdasar-hukum",
        "title": "Pertimbangan Hakim MK: Dalil Ijazah Palsu Gibran Tidak Beralasan Menurut Hukum",
        "author": "Angga Dwi Pratama",
        "published_at": "2024-04-22T16:15:00Z",
        "content": "Jakarta - Majelis Hakim MK menilai dalil pemohon mengenai dugaan kejanggalan riwayat pendidikan Gibran Rakabuming Raka tidak beralasan menurut hukum. Dokumen penyetaraan dari Kementerian Pendidikan serta konfirmasi resmi dari institusi pendidikan di Singapura dan Australia membuktikan keaslian riwayat pendidikan terlapor."
    },
    {
        "url": "https://nasional.tempo.co/read/1859001/reaksi-publik-dan-pengamat-hukum-tata-negara-atas-putusan-mk",
        "title": "Reaksi Publik dan Pakar Hukum Tata Negara atas Putusan Mahkamah Konstitusi",
        "author": "Fajar Pebrianto",
        "published_at": "2024-04-23T09:00:00Z",
        "content": "Putusan Mahkamah Konstitusi mengenai sengketa pilpres dan syarat ijazah memicu beragam respons di kalangan akademisi dan masyarakat sipil. Sebagian menilai putusan ini telah final dan mengikat secara konstitusional, sementara sebagian koalisi masyarakat sipil masih mengkritisi integritas pertimbangan hakim."
    }
]

SAMPLE_YOUTUBE_VIDEOS = [
    {
        "video_id": "mk_live_putusan_01",
        "title": "LIVE: Mahkamah Konstitusi Bacakan Putusan Gugatan Syarat dan Ijazah Gibran",
        "channel_title": "Kompas TV Official",
        "published_at": "2024-04-22T08:00:00Z"
    },
    {
        "video_id": "mk_live_putusan_02",
        "title": "Detik-Detik Putusan MK Terkait Keabsahan Ijazah dan Penetapan Cawapres",
        "channel_title": "CNN Indonesia TV",
        "published_at": "2024-04-22T11:30:00Z"
    }
]

SAMPLE_RAW_COMMENTS = [
    # Positif
    "Alhamdulillah akhirnya MK memutuskan secara adil dan tegas. Ijazah asli jangan lagi difitnah!",
    "Putusan hakim sudah sangat tepat dan sesuai aturan hukum. Sukses mas Gibran!",
    "Salut untuk majelis hakim MK yang berani membela kebenaran berdasarkan bukti autentik kampus.",
    "Bukti dari kemendikbud dan universitas singapura sudah resmi, mantap putusannya!",
    "Kebenaran pasti menang. Semoga bangsa kita sekarang bisa rukun dan damai kembali.",
    "Keputusan yang sangat bijak dan menenangkan rakyat. Hukum ditegakkan dengan adil.",
    "Mantul putusannya, sekarang mari kita kawal pembangunan Indonesia ke depan bersama pemuda cerdas.",
    "Sudah jelas terbukti sah secara hukum di persidangan terbuka, terima kasih hakim konstitusi.",
    "Dari awal memang cuma isu politik musiman, fakta hukum membuktikan ijazah asli dan legal.",
    "Keputusan berkelas! MK telah menunjukkan independensi dan profesionalitas luar biasa.",

    # Netral
    "Sidang putusan berlangsung lebih dari 5 jam dan disiarkan langsung di televisi.",
    "Apakah salinan lengkap amar putusan sudah bisa diunduh di website resmi MKRI?",
    "KPU menyatakan siap melaksanakan apapun instruksi dari amar putusan majelis hakim.",
    "Pertimbangan hukum dibacakan secara bergantian oleh sembilan hakim konstitusi.",
    "Menunggu konferensi pers dari tim hukum pemohon dan termohon sore hari ini.",
    "Sidang dihadiri perwakilan dari KPU, Bawaslu, serta para saksi ahli hukum tata negara.",
    "Bagaimana kelanjutan berkas administratif setelah putusan ini diumumkan oleh MK?",
    "Dokumen penyetaraan ijazah luar negeri memang memiliki mekanisme verifikasi tersendiri di kementerian.",
    "Ini baru tahap pembacaan putusan sengketa, proses pelantikan dijadwalkan bulan oktober.",
    "Kedua belah pihak saling menghormati jalannya persidangan di Mahkamah Konstitusi hari ini.",

    # Negatif
    "Sangat kecewa dengan putusan MK, hukum di negeri ini sudah rusak dan berpihak ke penguasa!",
    "Bohong semua ini, dokumen banyak yang janggal tapi dipaksakan lolos demi kepentingan dinasti.",
    "Hukum tumpul ke atas tajam ke bawah. Keadilan sudah mati di gedung Mahkamah Konstitusi.",
    "Dagelan politik yang memalukan! Keputusan sudah disetting dari awal, rakyat dibodoh-bodohi.",
    "Kecewa berat, tidak ada keberanian dari hakim untuk mengusut kejanggalan dokumen secara tuntas.",
    "Rusak parah demokrasi kita kalau institusi penegak hukum seperti ini terus dibiarkan.",
    "Gugatan ditolak begitu saja tanpa memeriksa saksi independen, sangat tidak adil!",
    "Publik tidak akan pernah percaya lagi dengan integritas MK setelah putusan cacat moral ini.",
    "Penjelasan hakim berbelit-belit dan tampak sekali menutup-nutupi fakta yang sebenarnya.",
    "Sedih melihat nasib hukum Indonesia, kebenaran dikalahkan oleh kekuasaan dan intrik politik."
]

def generate_mock_news_data():
    """Menghasilkan list dokumen berita mentah (format Bronze Layer)."""
    results = []
    for item in SAMPLE_NEWS_ARTICLES:
        doc = {
            "source": "news",
            "url": item["url"],
            "raw": {
                "title": item["title"],
                "content": item["content"],
                "author": item["author"],
                "published_at": item["published_at"],
                "url": item["url"]
            },
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
        results.append(doc)
    return results

def generate_mock_youtube_data(count: int = 40):
    """Menghasilkan list dokumen komentar YouTube mentah (format Bronze Layer)."""
    results = []
    authors = ["Budi Santoso", "Dewi Lestari", "Rian Pratama", "Siti Aminah", "Joko Widodo Fans",
               "Hendra Setiawan", "Rina Wulandari", "Agus Supriyanto", "Maya Indah", "Rizky Firmansyah"]
    
    for i in range(count):
        video = random.choice(SAMPLE_YOUTUBE_VIDEOS)
        comment_text = SAMPLE_RAW_COMMENTS[i % len(SAMPLE_RAW_COMMENTS)]
        # Tambahkan sedikit variasi gaya bahasa medsos / alay
        if random.random() > 0.5:
            comment_text = comment_text.replace("yang", "yg").replace("tidak", "gak").replace("banget", "bgt").replace("dengan", "dgn")
        
        doc = {
            "source": "youtube",
            "video_id": video["video_id"],
            "video_title": video["title"],
            "comment_id": f"yt_comm_{uuid.uuid4().hex[:12]}",
            "raw": {
                "text": comment_text,
                "author": random.choice(authors),
                "published_at": f"2024-04-{random.randint(22, 25):02d}T{random.randint(8, 20):02d}:{random.randint(10, 59):02d}:00Z",
                "like_count": random.choice([0, 1, 3, 7, 15, 42, 110, 250, 480])
            },
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }
        results.append(doc)
    return results
