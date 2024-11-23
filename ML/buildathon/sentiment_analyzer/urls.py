# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("analyze-tweet/", views.analyze_tweet, name="analyze_tweet"),
]
