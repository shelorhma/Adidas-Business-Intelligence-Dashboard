from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Ambil path dari folder DAG
dag_path = os.path.dirname(__file__)

def extract():
    df = pd.read_csv(os.path.join(dag_path, 'adidas_full_data.csv'))
    df.to_csv(os.path.join(dag_path, 'temp_adidas.csv'), index=False)

def transform():
    df = pd.read_csv(os.path.join(dag_path, 'temp_adidas.csv'))

    # Penjualan per Wilayah
    olap_region = df.groupby(['region', 'state', 'city']).agg({
        'sales_amount': 'sum',
        'units_sold': 'sum',
        'operating_profit': 'sum'
    }).reset_index()
    olap_region.to_csv(os.path.join(dag_path, 'olap_region.csv'), index=False)

    # Margin & Profit Produk 
    df['margin'] = df['operating_profit'] / df['cost_price']
    df['margin'] = df['margin'].replace([float('inf'), -float('inf')], 0).fillna(0)

    olap_profit = df.groupby(['product_id', 'product', 'category']).agg({
        'sales_amount': 'sum',
        'operating_profit': 'sum',
        'cost_price': 'mean',
        'margin': 'mean'
    }).reset_index()
    olap_profit.to_csv(os.path.join(dag_path, 'olap_profit.csv'), index=False)

    # Tren Penjualan Produk
    olap_trend = df.groupby(['date', 'product_id', 'category', 'season', 'time_period']).agg({
        'sales_amount': 'sum',
        'units_sold': 'sum',
        'profit_margin': 'mean',
        'growth_rate': 'mean'
    }).reset_index()
    olap_trend.to_csv(os.path.join(dag_path, 'olap_trend.csv'), index=False)

def load():
    print("Output CSV OLAP telah disimpan di folder DAG.")

with DAG(
    dag_id='etl_adidas_dashboard',
    start_date=datetime(2023, 1, 1),
    schedule='@daily',
    catchup=False,
    tags=['etl', 'adidas']
) as dag:

    t1 = PythonOperator(task_id='extract', python_callable=extract)
    t2 = PythonOperator(task_id='transform', python_callable=transform)
    t3 = PythonOperator(task_id='load', python_callable=load)

    t1 >> t2 >> t3
