from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [

    path('admin/', admin.site.urls),
    path('pedidos/', include('pedidos.urls')),
    path('clientes/', include('clientes.urls')),
    path('produtos/', include('produtos.urls')),
    path('categorias/', include('categorias.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
