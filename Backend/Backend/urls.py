from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/patients/', include('apps.patients.urls')),
    path('api/diaries/', include('apps.diaries.urls')),
    path('api/summaries/', include('apps.summaries.urls')),
]
