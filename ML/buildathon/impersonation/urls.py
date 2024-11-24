from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'celebrities', views.CelebrityViewSet)
router.register(r'impersonations', views.ImpersonationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate/', views.generate_impersonation, name='generate-impersonation'),
]
