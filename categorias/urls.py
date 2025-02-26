from django.urls import path
from categorias import views

urlpatterns = [
    path('categorias/', views.CategoriaListView.as_view(), name='categoria-list'),
    path('categorias/<slug:slug>/', views.CategoriaDetailView.as_view(), name='categoria-detail'),
    path('categorias/<slug:slug>/produtos/', views.CategoriaProdutosView.as_view(), name='categoria-produtos'),
    path('categorias/<slug:slug>/produtos/reordenar/', views.CategoriaProdutosView.as_view(), name='reordenar-produtos'),
]
