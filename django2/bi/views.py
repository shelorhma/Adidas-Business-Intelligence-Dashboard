from django.shortcuts import render
from bi.models import FactSalesRegion, FactProductProfit, FactSalesTrend
from plotly.offline import plot
import plotly.express as px
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from pandas.api.types import CategoricalDtype

def combined_dashboard(request):
    # --- Penjualan per Wilayah ---
    region_data = FactSalesRegion.objects.select_related('region').all()
    df_region = pd.DataFrame.from_records(region_data.values(
        'region__region', 'region__state', 'region__city',
        'sales_amount', 'units_sold', 'operating_profit',
    ))
    df_region.rename(columns={
        'region__region': 'region',
        'region__state': 'state',
        'region__city': 'city'
    }, inplace=True)

    if not df_region.empty:
        df_region_grouped = df_region.groupby(['region', 'state'])[['sales_amount', 'operating_profit']].sum().reset_index()
        fig_region = px.bar(
            df_region_grouped,
            x='region',
            y='sales_amount',
            color='state',
            title='Total Penjualan per Wilayah',
            text_auto=True
        )
        fig_region.update_layout(xaxis_title='Region', yaxis_title='Sales Amount', legend_title='State')
        plot_region = plot(fig_region, output_type='div')
        total_sales = df_region['sales_amount'].sum()
        total_profit = df_region['operating_profit'].sum()
        total_units_sold = df_region['units_sold'].sum()
    else:
        plot_region = "<p>Tidak ada data wilayah.</p>"
        total_sales = 0
        total_profit = 0
        total_units_sold = 0

    # --- Profit Produk per Kategori (pengganti margin) ---
    profit_data = FactProductProfit.objects.all()
    df_profit = pd.DataFrame.from_records(profit_data.values(
        'category', 'sales_amount', 'operating_profit', 'cost_price'
    ))

    if not df_profit.empty:
        df_profit_grouped = df_profit.groupby('category')[['operating_profit']].sum().reset_index()
        fig_profit = px.bar(
            df_profit_grouped,
            x='category',
            y='operating_profit',
            title='Total Profit per Kategori Produk',
            text_auto=True,
            color='category'
        )
        fig_profit.update_layout(xaxis_title='Kategori Produk', yaxis_title='Operating Profit', legend_title='Kategori')
        plot_profit = plot(fig_profit, output_type='div')
    else:
        plot_profit = "<p>Tidak ada data profit produk.</p>"

    # --- Tren dan Pertumbuhan Penjualan ---
    trend_data = FactSalesTrend.objects.select_related('date').values(
        'category', 'time_period', 'growth_rate', 'sales_amount', 'season', 'date__year'
    )
    df_trend = pd.DataFrame.from_records(trend_data)
    df_trend.rename(columns={'date__year': 'year'}, inplace=True)
    df_trend = df_trend[df_trend['year'].isin([2020, 2021])]

    if not df_trend.empty:
        df_trend_season = df_trend.groupby(['category', 'season'])[['growth_rate']].mean().reset_index()
        fig_trend = px.bar(
            df_trend_season,
            x='season',
            y='growth_rate',
            color='category',
            barmode='group',
            title='Rata-rata Pertumbuhan Penjualan per Musim (2020–2021)',
            text_auto=True
        )
        fig_trend.update_layout(xaxis_title='Season', yaxis_title='Growth Rate (%)', legend_title='Category')
        plot_trend = plot(fig_trend, output_type='div')
        growth_rate = round(df_trend['growth_rate'].mean(), 2)
    else:
        plot_trend = "<p>Tidak ada data tren penjualan.</p>"
        growth_rate = 0

    # --- Prediksi Penjualan Kuartal per Kategori ---
    if not df_trend.empty:
        df_trend['quarter_label'] = df_trend['year'].astype(str) + df_trend['time_period'].str.upper()
        quarter_order = CategoricalDtype(['Q1', 'Q2', 'Q3', 'Q4'], ordered=True)
        df_trend['time_period'] = df_trend['time_period'].str.upper().astype(quarter_order)

        df_trend_grouped = df_trend.groupby(['category', 'quarter_label', 'time_period'], observed=True)[
            ['sales_amount', 'growth_rate']
        ].mean().reset_index()
        df_trend_grouped['quarter_index'] = df_trend_grouped.groupby('category').cumcount()

        future_periods = 4
        df_forecast = df_trend_grouped[['category', 'quarter_index', 'sales_amount']].copy()
        predictions = []

        for cat in df_forecast['category'].unique():
            df_cat = df_forecast[df_forecast['category'] == cat].copy().sort_values('quarter_index')
            df_cat['period_num'] = np.arange(len(df_cat))

            model = LinearRegression()
            model.fit(df_cat[['period_num']], df_cat['sales_amount'])

            future_index = np.arange(len(df_cat), len(df_cat) + future_periods)
            start_index = df_cat['quarter_index'].max() + 1
            start_year = 2020
            future_labels = [f"{start_year + (i // 4)}Q{(i % 4) + 1}" for i in range(start_index, start_index + future_periods)]

            predicted_sales = model.predict(pd.DataFrame({'period_num': future_index}))
            df_pred = pd.DataFrame({
                'quarter_label': future_labels,
                'sales_amount': predicted_sales,
                'category': cat,
                'label': 'Prediksi'
            })

            df_cat['label'] = 'Aktual'
            df_cat['quarter_label'] = df_trend_grouped[df_trend_grouped['category'] == cat]['quarter_label'].tolist()
            df_cat_final = df_cat[['quarter_label', 'sales_amount', 'category', 'label']]

            predictions.append(pd.concat([df_cat_final, df_pred]))

        df_all = pd.concat(predictions)

        fig_forecast = px.line(
            df_all,
            x='quarter_label',
            y='sales_amount',
            color='category',
            line_dash='label',
            title='Prediksi Penjualan per Kategori (4 Kuartal Setelah 2021)',
            markers=True
        )
        fig_forecast.update_layout(xaxis_title='Quarter', yaxis_title='Sales', legend_title='Category & Label')
        plot_forecast = plot(fig_forecast, output_type='div')
    else:
        plot_forecast = "<p>Tidak ada data untuk prediksi penjualan.</p>"

    return render(request, 'dashboard/combined_dashboard.html', {
        'plot_region': plot_region,
        'plot_profit': plot_profit,
        'plot_trend': plot_trend,
        'plot_forecast': plot_forecast,
        'total_sales': f"{total_sales:,.0f}",
        'total_profit': f"{total_profit:,.0f}",
        'total_units_sold': f"{total_units_sold:,.0f}",
        'growth_rate': growth_rate
    })
