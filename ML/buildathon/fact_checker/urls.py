# fact_checker/urls.py
from django.urls import path
from .views import FactCheckView,SimpleGeminiChatView

urlpatterns = [
    path('fact-check/', FactCheckView.as_view(), name='fact-check'),
   # path('simple_gemini_chat/', SimpleGeminiChatView.as_view(), name='simple_gemini_chat'),
]   
