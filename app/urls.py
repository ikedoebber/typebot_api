from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from accounts.views import home
from django.contrib.auth.views import LogoutView


urlpatterns = [

    path("", home, name="home"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path('pedidos/', include('pedidos.urls')),
    path('clientes/', include('clientes.urls')),
    path('produtos/', include('produtos.urls')),
    path('categorias/', include('categorias.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
