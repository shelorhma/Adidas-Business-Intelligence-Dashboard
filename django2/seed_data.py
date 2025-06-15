import os
import django
import pandas as pd
from datetime import datetime

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from bi.models import Region, Product, Date, FactSalesRegion, FactProductProfit, FactSalesTrend

# Path ke folder 'dags'
DAGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dags')

# ======================
# OLAP 1: Penjualan per Wilayah
# ======================
df_region = pd.read_csv(os.path.join(DAGS_DIR, 'olap_region.csv'))
FactSalesRegion.objects.all().delete()

for _, row in df_region.iterrows():
    region_obj, _ = Region.objects.get_or_create(
        region=row['region'],
        state=row['state'],
        city=row['city'],
        defaults={
            'population': 1000000,
            'market_size': 'Medium',
            'average_income': 70000,
            'market_potential': 0.8,
            'growth_opportunity': 0.7,
        }
    )
    FactSalesRegion.objects.create(
        region=region_obj,
        state=row['state'],
        city=row['city'],
        sales_amount=row['sales_amount'],
        units_sold=row['units_sold'],
        operating_profit=row['operating_profit']
    )

# ======================
# OLAP 2: Margin & Profit Produk
# ======================
df_profit = pd.read_csv(os.path.join(DAGS_DIR, 'olap_profit.csv'))
FactProductProfit.objects.all().delete()

for _, row in df_profit.iterrows():
    try:
        product_obj = Product.objects.get(product_id=row['product_id'])
        FactProductProfit.objects.create(
            product=product_obj,
            category=row['category'],
            sales_amount=row['sales_amount'],
            operating_profit=row['operating_profit'],
            cost_price=row['cost_price'],
            margin=row['margin']
        )
    except Product.DoesNotExist:
        print(f"Produk dengan ID '{row['product_id']}' tidak ditemukan.")

# ======================
# OLAP 3: Tren Penjualan Produk
# ======================
df_trend = pd.read_csv(os.path.join(DAGS_DIR, 'olap_trend.csv'))
FactSalesTrend.objects.all().delete()

# Pastikan kolom 'date' dalam format datetime
df_trend['date'] = pd.to_datetime(df_trend['date'], errors='coerce')

for _, row in df_trend.iterrows():
    try:
        product_obj = Product.objects.get(product_id=row['product_id'])
        date_obj = Date.objects.get(date=row['date'].date())  # pastikan hanya tanggal

        FactSalesTrend.objects.create(
            date=date_obj,
            product=product_obj,
            category=row['category'],
            season=row['season'],
            time_period=row['time_period'],
            sales_amount=row['sales_amount'],
            units_sold=row['units_sold'],
            profit_margin=row['profit_margin'],
            growth_rate=row['growth_rate']
        )
    except Product.DoesNotExist:
        print(f"Produk dengan ID '{row['product_id']}' tidak ditemukan.")
    except Date.DoesNotExist:
        print(f"Tanggal '{row['date']}' tidak ditemukan di tabel Date.")
