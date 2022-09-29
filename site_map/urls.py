from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
      path('login', views.login_page, name='login'),
      path('logout', views.logout_user, name='logout'),
      path('register', views.register_page, name='register'),
      path('', views.home_page, name='home'),
      path('get_coords_and_profile', views.get_coords_and_profile),
      path('lk', views.lk, name='lk'),
      path('send', views.send_message)
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
