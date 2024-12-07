# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Endpoint for image analysis
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    
    # Optional health check endpoint
    path('health/', views.health_check, name='health_check')
]