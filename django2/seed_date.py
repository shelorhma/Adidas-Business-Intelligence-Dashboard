import os
import django
import pandas as pd

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from bi.models import Date

# Path ke file CSV sumber (di folder dags)
CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dags', 'adidas_full_data.csv')

# Baca data
df = pd.read_csv(CSV_PATH)

# Pastikan kolom date ada
if 'date' not in df.columns:
    raise Exception("Kolom 'date' tidak ditemukan dalam CSV.")

# Konversi kolom 'date' ke datetime
df['date'] = pd.to_datetime(df['date'])

# Ambil tanggal unik
unique_dates = df['date'].dropna().dt.date.unique()

# Hapus data lama (opsional)
Date.objects.all().delete()

# Helper fungsi untuk dapatkan season dan time_period
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Spring"
    elif month in [6, 7, 8]:
        return "Summer"
    else:
        return "Fall"

def get_time_period(hour):  # default jam 12 siang
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

# Masukkan ke tabel Date
for d in unique_dates:
    date_obj = pd.Timestamp(d)
    Date.objects.get_or_create(
        date=date_obj.date(),
        defaults={
            'month': date_obj.strftime('%B'),               # e.g., 'January'
            'year': date_obj.year,
            'season': get_season(date_obj.month),
            'is_holiday': date_obj.weekday() in [5, 6],     # Sabtu dan Minggu dianggap libur
            'time_period': get_time_period(12)              # Asumsikan penjualan jam 12 siang
        }
    )
