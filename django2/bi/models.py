from django.db import models

class Product(models.Model):
    product_id = models.CharField(max_length=50)
    product = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    subcategory = models.CharField(max_length=50)
    unit_price = models.FloatField()
    cost_price = models.FloatField()
    launch_date = models.DateField()
    performance_score = models.FloatField()

    def __str__(self):
        return self.product

class Region(models.Model):
    region = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    population = models.IntegerField()
    market_size = models.CharField(max_length=20)
    average_income = models.FloatField()
    market_potential = models.FloatField()
    growth_opportunity = models.FloatField()

class Store(models.Model):
    retailer = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    store_type = models.CharField(max_length=50)
    store_size = models.CharField(max_length=20)
    store_location = models.CharField(max_length=50)
    store_performance = models.FloatField()

class Date(models.Model):
    date = models.DateField()
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    season = models.CharField(max_length=20)
    is_holiday = models.BooleanField()
    time_period = models.CharField(max_length=20)

class FactSalesRegion(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    sales_amount = models.FloatField()
    units_sold = models.IntegerField()
    operating_profit = models.FloatField()

class FactProductProfit(models.Model):
    product = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    sales_amount = models.FloatField()
    operating_profit = models.FloatField()
    cost_price = models.FloatField()
    margin = models.FloatField()

class FactSalesTrend(models.Model):
    date = models.ForeignKey(Date, on_delete=models.CASCADE)
    product = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    season = models.CharField(max_length=20)
    time_period = models.CharField(max_length=20)
    sales_amount = models.FloatField()
    units_sold = models.IntegerField()
    profit_margin = models.FloatField()
    growth_rate = models.FloatField()
