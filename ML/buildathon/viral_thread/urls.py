from django.urls import path
from .views import GenerateThreadView

urlpatterns = [
    path('generate-thread/', GenerateThreadView.as_view(), name='generate-thread'),
]