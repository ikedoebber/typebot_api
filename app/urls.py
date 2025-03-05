from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from accounts.views import home
from accounts.views import register_view, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('pedidos/', include('pedidos.urls')),
    path('clientes/', include('clientes.urls')),
    path('produtos/', include('produtos.urls')),
    path('categorias/', include('categorias.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
