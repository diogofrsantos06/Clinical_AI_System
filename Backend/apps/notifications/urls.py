from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet

router = DefaultRouter()
# Usamos r'' (vazio) porque o prefixo 'api/notifications/' já foi dado no ficheiro principal
router.register(r'', NotificationViewSet, basename='notifications')

urlpatterns = [
    path('', include(router.urls)),
]