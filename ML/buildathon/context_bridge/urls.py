from django.urls import path
from .views import ProcessTweetView

urlpatterns = [
    path('process-tweet/', ProcessTweetView.as_view(), name='process-tweet'),
]