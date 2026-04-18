# Brazilian E-Commerce Dashboard

Dashboard analisis data berbasis Streamlit untuk dataset Olist E-Commerce.

## 🔗 Live Dashboard
https://projeknanikerawati.streamlit.app/

## Cara Menjalankan

### 1. Clone repository
```bash
git clone https://github.com/username/nama-repo.git
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Masuk ke folder project
```bash
cd Downloads/Submission
```

### 4. Jalankan dashboard
```bash
streamlit run dashboard/dashboard.py
```

### 5. Buka browser
Otomatis terbuka di `http://localhost:8501`

## Fitur Dashboard

- **KPI Cards** — Total pesanan, revenue, item terjual, avg order value
- **Filter Sidebar** — Rentang tanggal & kategori produk
- **Analisis Kategori** — Top N kategori berdasarkan volume & revenue
- **Pola Waktu** — Bar chart jam/hari + heatmap hari × jam
- **Segmentasi RFM** — Bar chart segmen, scatter plot, tabel ringkasan

## Struktur Folder

```
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   ├── olist_orders_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_products_dataset.csv
│   └── product_category_name_translation.csv
├── notebook.ipynb
├── requirements.txt
├── url.txt
└── README.md
```