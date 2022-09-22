from django.contrib import admin
from django.urls import path, include
import project

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('site_map.urls'))
]
