import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide"
)

# ─────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(
        os.path.join(base_dir, "main_data.csv"),
        parse_dates=["order_purchase_timestamp"]
    )
    return df

@st.cache_data
def compute_rfm(df):
    reference_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        recency=("order_purchase_timestamp", lambda x: (reference_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum")
    ).reset_index()

    rfm["R_score"] = pd.qcut(rfm["recency"], q=5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]

    def segment(row):
        r, f = row["R_score"], row["F_score"]
        score = row["RFM_score"]
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "Recent Customers"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2 and row["M_score"] >= 4:
            return "Lost High Value"
        elif score >= 11:
            return "Potential Loyalist"
        elif score >= 7:
            return "Needs Attention"
        else:
            return "Hibernating"

    rfm["segment"] = rfm.apply(segment, axis=1)
    return rfm

df_clean = load_data()
rfm = compute_rfm(df_clean)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
st.sidebar.title("🛒 E-Commerce Dashboard")
st.sidebar.markdown("**Olist Brazilian E-Commerce**")
st.sidebar.markdown("---")

st.sidebar.title("🔎 Filter Data")

min_date = df_clean["order_purchase_timestamp"].min().date()
max_date = df_clean["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Waktu Analisis (2017–2018)",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

st.sidebar.markdown("---")

st.sidebar.title("📋 Pilih Analisis")
show_kategori = st.sidebar.checkbox(
    "📦 Volume & Revenue Tertinggi (2017–2018)", value=True
)
show_waktu = st.sidebar.checkbox(
    "⏰ Pola Waktu Pemesanan (2017–2018)", value=True
)
show_rfm = st.sidebar.checkbox(
    "👥 Segmentasi Pelanggan RFM (2017–2018)", value=True
)

st.sidebar.markdown("---")
st.sidebar.caption("📊 Data: Olist Brazilian E-Commerce")
st.sidebar.caption("👤 Nanik Erawati_CDCC284D6X2024")

# ─────────────────────────────────────────
# TERAPKAN FILTER — dengan try-except
# ─────────────────────────────────────────
try:
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df_clean[
            (df_clean["order_purchase_timestamp"].dt.date >= start_date) &
            (df_clean["order_purchase_timestamp"].dt.date <= end_date)
        ]
    else:
        st.warning("⚠️ Pilih rentang tanggal lengkap (tanggal awal dan akhir).")
        df_filtered = df_clean.copy()
except Exception as e:
    st.error(f"❌ Error pada filter tanggal: {e}")
    df_filtered = df_clean.copy()

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🛒 Brazilian E-Commerce Dashboard")
st.markdown(
    "Analisis performa penjualan, pola waktu pemesanan, dan segmentasi pelanggan "
    "berbasis data **Olist E-Commerce** periode **2017–2018**."
)
st.markdown("---")

# ─────────────────────────────────────────
# SECTION 1 — KPI CARDS
# ─────────────────────────────────────────
st.subheader("📌 Overview Performa (2017–2018)")

total_orders  = df_filtered["order_id"].nunique()
total_revenue = df_filtered["price"].sum()
total_items   = len(df_filtered)
avg_order_val = df_filtered.groupby("order_id")["price"].sum().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total Pesanan",       f"{total_orders:,}")
col2.metric("💰 Total Revenue",       f"R${total_revenue:,.0f}")
col3.metric("📦 Total Item Terjual",  f"{total_items:,}")
col4.metric("🛍️ Avg. Order Value",   f"R${avg_order_val:,.2f}")

st.markdown("---")

# ─────────────────────────────────────────
# SECTION 2 — KATEGORI PRODUK
# ─────────────────────────────────────────
if show_kategori:
    st.subheader("📦 Pertanyaan 1: Kategori Produk dengan Volume & Revenue Tertinggi (2017–2018)")

    product_performance = df_filtered.groupby("product_category_name_english").agg(
        order_count=("order_id", "nunique"),
        revenue=("price", "sum")
    ).reset_index()

    top_n = st.slider("Tampilkan Top N Kategori", min_value=5, max_value=20, value=10, step=1)

    top_volume  = product_performance.sort_values("order_count", ascending=False).head(top_n)
    top_revenue = product_performance.sort_values("revenue", ascending=False).head(top_n)

    fig1 = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"Top {top_n} Kategori — Volume Penjualan (2017–2018)",
            f"Top {top_n} Kategori — Revenue Terbesar (2017–2018)"
        )
    )

    colors_vol = ["#0077b6" if i == 0 else "#adb5bd" for i in range(len(top_volume))]
    fig1.add_trace(
        go.Bar(
            x=top_volume["order_count"].iloc[::-1],
            y=top_volume["product_category_name_english"].iloc[::-1],
            orientation="h",
            marker_color=colors_vol[::-1],
            text=top_volume["order_count"].iloc[::-1].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Pesanan: %{x:,}<extra></extra>",
            name="Volume"
        ),
        row=1, col=1
    )

    colors_rev = ["#e67e22" if i == 0 else "#adb5bd" for i in range(len(top_revenue))]
    fig1.add_trace(
        go.Bar(
            x=top_revenue["revenue"].iloc[::-1],
            y=top_revenue["product_category_name_english"].iloc[::-1],
            orientation="h",
            marker_color=colors_rev[::-1],
            text=top_revenue["revenue"].iloc[::-1].apply(lambda v: f"R${v:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Revenue: R$%{x:,.0f}<extra></extra>",
            name="Revenue"
        ),
        row=1, col=2
    )

    fig1.update_layout(
        title_text="Performa Kategori Produk: Volume vs Revenue (2017–2018)",
        title_font_size=18,
        showlegend=False,
        height=500
    )
    fig1.update_xaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("📝 Insight Kategori Produk"):
        st.markdown("""
        - Selama **periode 2017–2018**, **bed_bath_table** memimpin volume penjualan
          sebagai penggerak utama transaksi harian.
        - **health_beauty** & **watches_gifts** unggul di sisi revenue karena harga
          per unit yang lebih tinggi.
        - **Implikasi bisnis:** Strategi stok & promosi harus dibedakan antara
          *volume-driven* dan *revenue-driven* kategori.
        """)

    st.markdown("---")

# ─────────────────────────────────────────
# SECTION 3 — POLA WAKTU
# ─────────────────────────────────────────
if show_waktu:
    st.subheader("⏰ Pertanyaan 2: Jam & Hari Paling Aktif untuk Pemesanan (2017–2018)")

    df_filtered = df_filtered.copy()
    df_filtered["order_hour"] = df_filtered["order_purchase_timestamp"].dt.hour
    df_filtered["order_day"]  = df_filtered["order_purchase_timestamp"].dt.day_name()

    hourly_orders = df_filtered.groupby("order_hour")["order_id"].nunique().reset_index()
    hourly_orders.rename(columns={"order_id": "order_count"}, inplace=True)

    days_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    daily_orders = df_filtered.groupby("order_day")["order_id"].nunique().reindex(days_order).reset_index()
    daily_orders.rename(columns={"order_id": "order_count"}, inplace=True)

    peak_hour = hourly_orders.loc[hourly_orders["order_count"].idxmax(), "order_hour"]
    peak_day  = daily_orders.loc[daily_orders["order_count"].idxmax(), "order_day"]

    fig2 = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Distribusi Pesanan per Jam (2017–2018)",
            "Distribusi Pesanan per Hari (2017–2018)"
        )
    )

    colors_hour = ["#0077b6" if h == peak_hour else "#adb5bd"
                   for h in hourly_orders["order_hour"]]
    fig2.add_trace(
        go.Bar(
            x=hourly_orders["order_hour"],
            y=hourly_orders["order_count"],
            marker_color=colors_hour,
            hovertemplate="Jam %{x}:00<br>Pesanan: %{y:,}<extra></extra>",
            name="Per Jam"
        ),
        row=1, col=1
    )

    colors_day = ["#e67e22" if d == peak_day else "#adb5bd"
                  for d in daily_orders["order_day"]]
    fig2.add_trace(
        go.Bar(
            x=daily_orders["order_day"],
            y=daily_orders["order_count"],
            marker_color=colors_day,
            hovertemplate="<b>%{x}</b><br>Pesanan: %{y:,}<extra></extra>",
            name="Per Hari"
        ),
        row=1, col=2
    )

    fig2.update_layout(
        title_text="Pola Waktu Pemesanan Pelanggan (2017–2018)",
        title_font_size=18,
        showlegend=False,
        height=450
    )
    fig2.update_yaxes(showgrid=True, gridcolor="#eee")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("##### 🔥 Heatmap Kepadatan Pemesanan (Hari × Jam) — 2017–2018")

    heatmap_data = df_filtered.groupby(
        ["order_day", "order_hour"]
    )["order_id"].nunique().unstack(fill_value=0)
    heatmap_data = heatmap_data.reindex(days_order)

    fig3 = px.imshow(
        heatmap_data,
        color_continuous_scale="YlOrRd",
        labels={"x": "Jam", "y": "Hari", "color": "Jumlah Pesanan"},
        title="Heatmap Kepadatan Waktu Pemesanan (Hari × Jam) — 2017–2018"
    )
    fig3.update_layout(height=400, title_font_size=16)
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📝 Insight Pola Waktu"):
        st.markdown("""
        - Selama **periode 2017–2018**, puncak pemesanan terjadi antara
          **pukul 10:00–17:00**, dengan jam tertinggi di sekitar pukul 14:00–16:00.
        - **Senin & Selasa** adalah hari paling aktif; **Sabtu & Minggu** paling sepi.
        - **Implikasi bisnis:** Jadwalkan flash sale, push notification, dan kampanye
          iklan di rentang jam tersebut untuk memaksimalkan konversi.
        """)

    st.markdown("---")

# ─────────────────────────────────────────
# SECTION 4 — RFM
# ─────────────────────────────────────────
if show_rfm:
    st.subheader("👥 Analisis Lanjutan: Segmentasi Pelanggan RFM (2017–2018)")

    segment_colors = {
        "Champions":          "#0077b6",
        "Loyal Customers":    "#00b4d8",
        "Recent Customers":   "#90e0ef",
        "Potential Loyalist": "#52b788",
        "Needs Attention":    "#f4a261",
        "At Risk":            "#e63946",
        "Lost High Value":    "#9d0208",
        "Hibernating":        "#adb5bd"
    }

    col_r1, col_r2, col_r3 = st.columns(3)
    col_r1.metric("👥 Total Pelanggan Unik", f"{len(rfm):,}")
    col_r2.metric("🏆 Champions",
                  f"{len(rfm[rfm['segment'] == 'Champions']):,}")
    col_r3.metric("⚠️ At Risk + Lost",
                  f"{len(rfm[rfm['segment'].isin(['At Risk','Lost High Value'])]):,}")

    segment_counts   = rfm["segment"].value_counts().reset_index()
    segment_counts.columns = ["segment", "count"]
    segment_monetary = rfm.groupby("segment")["monetary"].mean().reset_index()
    segment_monetary = segment_monetary.sort_values("monetary", ascending=False)

    fig4 = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Jumlah Pelanggan per Segmen (2017–2018)",
            "Rata-rata Monetary per Segmen (2017–2018)"
        )
    )

    fig4.add_trace(
        go.Bar(
            x=segment_counts["count"].iloc[::-1],
            y=segment_counts["segment"].iloc[::-1],
            orientation="h",
            marker_color=[segment_colors.get(s, "#adb5bd")
                          for s in segment_counts["segment"].iloc[::-1]],
            text=segment_counts["count"].iloc[::-1].apply(lambda v: f"{v:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Pelanggan: %{x:,}<extra></extra>",
            name="Jumlah"
        ),
        row=1, col=1
    )

    fig4.add_trace(
        go.Bar(
            x=segment_monetary["monetary"].iloc[::-1],
            y=segment_monetary["segment"].iloc[::-1],
            orientation="h",
            marker_color=[segment_colors.get(s, "#adb5bd")
                          for s in segment_monetary["segment"].iloc[::-1]],
            text=segment_monetary["monetary"].iloc[::-1].apply(lambda v: f"R${v:,.0f}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Avg: R$%{x:,.0f}<extra></extra>",
            name="Monetary"
        ),
        row=1, col=2
    )

    fig4.update_layout(
        title_text="Analisis Segmentasi Pelanggan RFM (2017–2018)",
        title_font_size=18,
        showlegend=False,
        height=500
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.markdown("##### 🔵 Sebaran Pelanggan: Recency vs Monetary (2017–2018)")

    fig5 = px.scatter(
        rfm,
        x="recency",
        y="monetary",
        color="segment",
        color_discrete_map=segment_colors,
        hover_data=["frequency", "RFM_score"],
        labels={
            "recency":  "Recency (hari)",
            "monetary": "Monetary (BRL)",
            "segment":  "Segmen"
        },
        title="Sebaran Pelanggan: Recency vs Monetary (2017–2018)",
        opacity=0.6,
        height=500
    )
    fig5.update_traces(marker_size=6)
    fig5.update_layout(title_font_size=16)
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("##### 📋 Ringkasan Statistik per Segmen (2017–2018)")

    rfm_summary = rfm.groupby("segment").agg(
        Jumlah_Pelanggan=("customer_id", "count"),
        Avg_Recency=("recency", "mean"),
        Avg_Frequency=("frequency", "mean"),
        Avg_Monetary=("monetary", "mean"),
        Total_Revenue=("monetary", "sum")
    ).round(1).reset_index().sort_values("Total_Revenue", ascending=False)

    rfm_summary.columns = [
        "Segmen", "Jml Pelanggan",
        "Avg Recency (hari)", "Avg Frequency",
        "Avg Monetary (BRL)", "Total Revenue (BRL)"
    ]
    st.dataframe(rfm_summary, use_container_width=True)

    with st.expander("📝 Insight RFM & Rekomendasi Bisnis"):
        st.markdown("""
        | Segmen | Strategi |
        |--------|----------|
        | **Champions** | Loyalty program, early access produk baru |
        | **Loyal Customers** | Reward poin, referral program |
        | **Recent Customers** | Welcome email series, cross-sell |
        | **Potential Loyalist** | Nudge pembelian kedua, promo bundling |
        | **Needs Attention** | Re-engagement campaign, reminder |
        | **At Risk** | Diskon terbatas waktu, survei kepuasan |
        | **Lost High Value** | Win-back campaign agresif |
        | **Hibernating** | Email reaktivasi atau exclude dari list aktif |
        """)

st.markdown("---")
st.caption("© 2026 · Dicoding Submission · Brazilian E-Commerce Analysis")