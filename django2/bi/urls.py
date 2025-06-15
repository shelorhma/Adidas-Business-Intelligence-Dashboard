from django.urls import path
from bi import views

urlpatterns = [
    path('', views.combined_dashboard, name='dashboard_home'),
]
