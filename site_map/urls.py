from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
                  path('login', views.login_page, name='login'),
                  path('logout', views.login_page, name='logout'),
                  path('register', views.register_page, name='register'),
                  path('', views.home_page, name='home'),
                  path('get_register', views.get_register)
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
