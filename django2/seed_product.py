import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from bi.models import Product

# Path ke file sumber (di folder dags)
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dags', 'adidas_full_data.csv')

# Baca data utama
df = pd.read_csv(CSV_PATH)

# Pastikan semua kolom yang dibutuhkan tersedia
required_cols = [
    'product_id', 'product', 'category', 'subcategory',
    'unit_price', 'cost_price', 'launch_date', 'performance_score'
]

# Validasi kolom
missing_cols = set(required_cols) - set(df.columns)
if missing_cols:
    raise ValueError(f"❌ Kolom berikut tidak ditemukan di CSV: {missing_cols}")

# Drop duplikat berdasarkan product_id
df_unique = df[required_cols].drop_duplicates()

# Convert tanggal (jika perlu)
df_unique['launch_date'] = pd.to_datetime(df_unique['launch_date'], errors='coerce')

# Isi ke tabel Product
for _, row in df_unique.iterrows():
    Product.objects.get_or_create(
        product_id=row['product_id'],
        defaults={
            'product': row['product'],
            'category': row['category'],
            'subcategory': row['subcategory'],
            'unit_price': row['unit_price'],
            'cost_price': row['cost_price'],
            'launch_date': row['launch_date'],
            'performance_score': row['performance_score']
        }
    )
