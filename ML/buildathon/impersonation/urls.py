from django.urls import path
from . import views

urlpatterns = [
    path('celebrities/', views.list_celebrities, name='list-celebrities'),
    path('impersonations/', views.list_impersonations, name='list-impersonations'),
    path('generate/', views.generate_impersonation, name='generate-impersonation'),
]
