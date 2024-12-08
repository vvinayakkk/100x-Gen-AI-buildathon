from django.urls import path
from . import views

urlpatterns = [
    path('summarize-comments/', views.summarize_tweet_comments, name='summarize_comments'),
]