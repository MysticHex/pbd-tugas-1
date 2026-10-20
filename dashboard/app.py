"""
Dashboard Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran
Menggunakan Streamlit, Plotly, dan terhubung langsung ke MongoDB (Bronze, Silver, Gold Layer).
"""
import sys
from pathlib import Path
from datetime import datetime

# Pastikan root workspace terdaftar di sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import (
    get_mongo_db,
    check_mongo_connection,
    resolve_mongo_uri,
    COLLECTION_BRONZE_YOUTUBE,
    COLLECTION_BRONZE_NEWS,
    COLLECTION_SILVER_COMMENTS,
    COLLECTION_SILVER_NEWS,
    COLLECTION_GOLD_SENTIMENT
)
from pipeline.bronze import get_bronze_stats
from pipeline.silver import get_silver_stats
from pipeline.gold import get_gold_analytics_summary, get_top_keywords

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Analisis Sentimen Putusan MK Ijazah Gibran",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.2rem 0;
    }
    .kpi-desc {
        font-size: 0.8rem;
        color: #94A3B8;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-pos { background-color: #DCFCE7; color: #166534; }
    .badge-neu { background-color: #FEF3C7; color: #92400E; }
    .badge-neg { background-color: #FEE2E2; color: #991B1B; }

    .comment-box {
        background: #F8FAFC;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-left: 4px solid #CBD5E1;
    }
    .comment-box.pos { border-left-color: #22C55E; }
    .comment-box.neu { border-left-color: #F59E0B; }
    .comment-box.neg { border-left-color: #EF4444; }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/scales--v1.png", width=64)
    st.markdown("### **Big Data Pipeline Monitor**")
    
    is_connected = check_mongo_connection()
    if is_connected:
        st.success("🟢 **MongoDB Terhubung**")
        st.caption(f"Host: `{resolve_mongo_uri()}`")
        st.caption("Docker Volume: `pbd_mongo_data` (WSL)")
    else:
        st.error("🔴 **MongoDB Terputus**")
        st.warning("Pastikan container `pbd_mongodb` aktif di WSL.")

    st.markdown("---")
    st.subheader("🛠️ Live Pipeline Runner")
    st.caption("Memicu pipeline langsung dari dashboard:")

    custom_urls_input = st.text_area(
        "Crawl Video Spesifik:",
        placeholder="https://youtu.be/CADyQAqFgo0\nhttps://youtu.be/I-Jd0XHw3Go",
        help="Masukkan URL atau ID video YouTube (satu per baris)"
    )
    if st.button("📥 Ambil Komentar Video di Atas", use_container_width=True):
        target_urls = [u.strip() for u in custom_urls_input.split() if u.strip()]
        if target_urls:
            with st.spinner(f"Mengambil komentar dari {len(target_urls)} video..."):
                from collectors.youtube_api import collect_youtube_data
                from pipeline.bronze import save_bronze_youtube
                from pipeline.silver import process_bronze_to_silver_comments
                from pipeline.gold import process_silver_to_gold

                comms = collect_youtube_data(video_ids=target_urls)
                ins, dup = save_bronze_youtube(comms)
                process_bronze_to_silver_comments()
                process_silver_to_gold()
                st.success(f"Berhasil! {ins} komentar baru disimpan ({dup} duplikat).")
                st.rerun()
        else:
            st.warning("Masukkan minimal satu URL video YouTube.")

    if st.button("🚀 Jalankan Full Pipeline (Crawl -> Gold)", use_container_width=True):
        with st.spinner("Menjalankan pipeline end-to-end..."):
            from collectors.youtube_api import collect_youtube_data
            from collectors.news_scraper import collect_news_data
            from pipeline.bronze import save_bronze_youtube, save_bronze_news
            from pipeline.silver import process_bronze_to_silver_comments, process_bronze_to_silver_news
            from pipeline.gold import process_silver_to_gold

            # 1. Crawl
            comms = collect_youtube_data(count=40)
            news = collect_news_data(count=3)
            save_bronze_youtube(comms)
            save_bronze_news(news)

            # 2. Process Silver
            process_bronze_to_silver_comments()
            process_bronze_to_silver_news()

            # 3. Analyze Gold
            process_silver_to_gold()

            st.success("✅ Pipeline selesai dieksekusi!")
            st.rerun()

    if st.button("🔄 Refresh Data Dashboard", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("""
    **Metadata Tugas:**
    - Mata Kuliah: Pengelolaan Big Data
    - NoSQL Database: MongoDB
    - Sumber Data: YouTube API & Website Scrapling
    - Arsitektur: Bronze → Silver → Gold
    """)

# ----------------- MAIN CONTENT -----------------
st.markdown('<div class="main-title">Analisis Sentimen Publik terhadap Putusan MK terkait Ijazah Gibran</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Pemantauan Opini Publik & Konteks Pemberitaan Media Nasional secara End-to-End</div>', unsafe_allow_html=True)

if not is_connected:
    st.error("Tidak dapat memuat visualisasi karena MongoDB belum aktif. Silakan jalankan `docker compose up -d` di WSL.")
    st.stop()

# Ambil data dari MongoDB
db = get_mongo_db()
gold_summary = get_gold_analytics_summary()
bronze_stats = get_bronze_stats()
silver_stats = get_silver_stats()

total_comments = gold_summary["total"]
total_articles = bronze_stats["bronze_news"]

# ----------------- SECTION 1: KPI CARDS -----------------
st.markdown("### 📊 Ringkasan Indikator Utama (KPI)")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Opini Publik</div>
        <div class="kpi-value" style="color: #1E293B;">{total_comments:,}</div>
        <div class="kpi-desc">Komentar Teranalisis</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sentimen Positif</div>
        <div class="kpi-value" style="color: #16A34A;">{gold_summary['positive']:,}</div>
        <div class="kpi-desc">{gold_summary['positive_pct']}% dari total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sentimen Netral</div>
        <div class="kpi-value" style="color: #D97706;">{gold_summary['neutral']:,}</div>
        <div class="kpi-desc">{gold_summary['neutral_pct']}% dari total</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Sentimen Negatif</div>
        <div class="kpi-value" style="color: #DC2626;">{gold_summary['negative']:,}</div>
        <div class="kpi-desc">{gold_summary['negative_pct']}% dari total</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Artikel Berita</div>
        <div class="kpi-value" style="color: #2563EB;">{total_articles:,}</div>
        <div class="kpi-desc">Konteks Scrapling</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

if total_comments == 0:
    st.info("💡 Belum ada data di Gold Layer. Silakan klik tombol **'Jalankan Full Pipeline'** di sidebar kiri atau jalankan `python main.py --step all` di terminal.")
    st.stop()

# ----------------- SECTION 2 & 3: CHARTS -----------------
col_chart_left, col_chart_right = st.columns([1, 1.4])

with col_chart_left:
    st.markdown("#### 🎯 Distribusi Sentimen Publik")
    dist_df = pd.DataFrame({
        "Sentimen": ["Positif", "Netral", "Negatif"],
        "Jumlah": [gold_summary["positive"], gold_summary["neutral"], gold_summary["negative"]],
        "Color": ["#22C55E", "#F59E0B", "#EF4444"]
    })

    fig_donut = px.pie(
        dist_df,
        names="Sentimen",
        values="Jumlah",
        hole=0.55,
        color="Sentimen",
        color_discrete_map={"Positif": "#22C55E", "Netral": "#F59E0B", "Negatif": "#EF4444"}
    )
    fig_donut.update_traces(textposition="inside", textinfo="percent+label", hoverinfo="label+value+percent")
    fig_donut.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_chart_right:
    st.markdown("#### 📈 Tren Sentimen dari Waktu ke Waktu")
    gold_records = list(db[COLLECTION_GOLD_SENTIMENT].find({}, {"published_at": 1, "sentiment": 1, "_id": 0}))
    df_timeline = pd.DataFrame(gold_records)

    if not df_timeline.empty and "published_at" in df_timeline.columns:
        # Konversi format tanggal
        df_timeline["date"] = pd.to_datetime(df_timeline["published_at"], errors="coerce").dt.date
        df_timeline = df_timeline.dropna(subset=["date"])
        
        timeline_grouped = df_timeline.groupby(["date", "sentiment"]).size().reset_index(name="count")
        
        fig_line = px.line(
            timeline_grouped,
            x="date",
            y="count",
            color="sentiment",
            color_discrete_map={"positive": "#22C55E", "neutral": "#F59E0B", "negative": "#EF4444"},
            markers=True,
            labels={"date": "Tanggal", "count": "Jumlah Komentar", "sentiment": "Sentimen"}
        )
        fig_line.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            xaxis_title="",
            yaxis_title="Volume Opini",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("Data waktu publikasi belum mencukupi untuk membuat timeline.")

# ----------------- SECTION 4 & 5: KEYWORDS & SOURCE -----------------
col_kw, col_src = st.columns([1.3, 1])

with col_kw:
    st.markdown("#### 🔍 Frekuensi Kata Kunci Terbanyak")
    kw_filter = st.radio("Filter Sentimen Kata:", ["Semua", "positive", "neutral", "negative"], horizontal=True, index=0)
    filter_val = None if kw_filter == "Semua" else kw_filter
    
    top_kw = get_top_keywords(limit=12, sentiment_filter=filter_val)
    if top_kw:
        df_kw = pd.DataFrame(top_kw, columns=["Kata Kunci", "Frekuensi"]).sort_values(by="Frekuensi", ascending=True)
        fig_bar = px.bar(
            df_kw,
            x="Frekuensi",
            y="Kata Kunci",
            orientation="h",
            color="Frekuensi",
            color_continuous_scale="Blues"
        )
        fig_bar.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, yaxis_title="")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Belum ada kata kunci yang dapat diekstrak.")

with col_src:
    st.markdown("#### 🌐 Arsitektur Data Layer Storage")
    storage_df = pd.DataFrame([
        {"Layer": "Bronze (Raw YouTube)", "Total Dokumen": bronze_stats["bronze_youtube"]},
        {"Layer": "Bronze (Raw News)", "Total Dokumen": bronze_stats["bronze_news"]},
        {"Layer": "Silver (Clean Comments)", "Total Dokumen": silver_stats["silver_comments"]},
        {"Layer": "Silver (Clean News)", "Total Dokumen": silver_stats["silver_news"]},
        {"Layer": "Gold (Analyzed Sentiment)", "Total Dokumen": total_comments}
    ])
    fig_storage = px.bar(
        storage_df,
        x="Layer",
        y="Total Dokumen",
        color="Layer",
        text="Total Dokumen",
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig_storage.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False, xaxis_title="", yaxis_title="Jumlah Dokumen")
    st.plotly_chart(fig_storage, use_container_width=True)

# ----------------- SECTION 6: EXPLORER KOMENTAR -----------------
st.markdown("### 💬 Penjelajah Komentar Publik (Comment Explorer)")

col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
with col_f1:
    filter_sentiment = st.selectbox("Filter Sentimen:", ["Semua", "positive", "neutral", "negative"], index=0)
with col_f2:
    min_confidence = st.slider("Minimum Confidence:", min_value=0.5, max_value=1.0, value=0.6, step=0.05)
with col_f3:
    search_keyword = st.text_input("Cari Kata Kunci Komentar:", placeholder="Contoh: asli, sidang, mk...")

query_filter = {"confidence": {"$gte": min_confidence}}
if filter_sentiment != "Semua":
    query_filter["sentiment"] = filter_sentiment
if search_keyword.strip():
    query_filter["text_clean"] = {"$regex": search_keyword.strip(), "$options": "i"}

filtered_comments = list(db[COLLECTION_GOLD_SENTIMENT].find(
    query_filter,
    {"_id": 0, "comment_id": 1, "author": 1, "text_original": 1, "sentiment": 1, "confidence": 1, "like_count": 1, "published_at": 1}
).sort("like_count", -1).limit(30))

st.caption(f"Menampilkan {len(filtered_comments)} komentar teratas:")

if filtered_comments:
    for item in filtered_comments:
        s_class = item["sentiment"]
        badge_style = "badge-pos" if s_class == "positive" else ("badge-neu" if s_class == "neutral" else "badge-neg")
        box_style = "pos" if s_class == "positive" else ("neu" if s_class == "neutral" else "neg")
        s_label = s_class.upper()
        conf_pct = int(item.get("confidence", 0) * 100)
        likes = item.get("like_count", 0)
        author = item.get("author", "Anonim")
        pub_date = str(item.get("published_at", ""))[:10]

        st.markdown(f"""
        <div class="comment-box {box_style}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 600; font-size: 0.9rem; color: #334155;">👤 {author} <span style="font-size: 0.8rem; color: #94A3B8;">({pub_date})</span></span>
                <div>
                    <span class="status-badge {badge_style}">{s_label} ({conf_pct}%)</span>
                    <span style="margin-left: 8px; font-size: 0.8rem; color: #64748B;">👍 {likes}</span>
                </div>
            </div>
            <div style="font-size: 0.95rem; color: #1E293B;">"{item.get('text_original', '')}"</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Tidak ada komentar yang cocok dengan filter yang dipilih.")

# ----------------- SECTION 7: ARTIKEL BERITA (KONTEKS) -----------------
with st.expander("📰 Lihat Artikel Berita Konteks (Scrapling Web Scraper)"):
    news_docs = list(db[COLLECTION_SILVER_NEWS].find({}, {"_id": 0}).limit(10))
    if news_docs:
        for n in news_docs:
            st.markdown(f"**[{n.get('title', 'Berita')}]({n.get('url', '#')})**")
            st.caption(f"Penulis: {n.get('author', 'Redaksi')} | Tanggal: {n.get('published_at', '')}")
            st.write(n.get("content", "")[:300] + "...")
            st.divider()
    else:
        st.caption("Belum ada data artikel berita di Silver Layer.")
