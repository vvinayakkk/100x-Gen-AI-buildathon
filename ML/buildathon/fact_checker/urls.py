# fact_checker/urls.py
from django.urls import path
from .views import FactCheckView

urlpatterns = [
    path('fact-check/', FactCheckView.as_view(), name='fact-check'),
]   