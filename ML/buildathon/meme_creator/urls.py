from django.urls import path
from . import views

urlpatterns = [
    path('generate-meme/', views.generate_meme, name='generate-meme'),
]