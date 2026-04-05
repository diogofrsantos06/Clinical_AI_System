from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClinicalDiaryViewSet

router = DefaultRouter()
router.register(r'', ClinicalDiaryViewSet, basename='diary')

urlpatterns = [
    path('', include(router.urls)),
]