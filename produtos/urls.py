from django.urls import path
from produtos.views import ProdutoListCreateView, ProdutoAtivosListView, ProdutoRetrieveUpdateDestroyView , LanchesAPIView, PorcoesAPIView, AdicionaisAPIView, BebidasAPIView, ProdutoDetalheAPIView


urlpatterns = [
    path('produtos/list-create/', ProdutoListCreateView.as_view(), name='produto-list-create'),
    path('produtos/<int:pk>/detail/', ProdutoRetrieveUpdateDestroyView.as_view(), name='produto-detail-full'),
    path('produtos/ativos/', ProdutoAtivosListView.as_view(), name='produto-ativos'),

    path('api/lanches/', LanchesAPIView.as_view(), name='api-lanches'),
    path('api/porcoes/', PorcoesAPIView.as_view(), name='api-porcoes'),
    path('api/adicionais/', AdicionaisAPIView.as_view(), name='api-adicionais'),
    path('api/bebidas/', BebidasAPIView.as_view(), name='api-bebidas'),
    path("api/produto/<int:codigo>/", ProdutoDetalheAPIView.as_view(), name="produto-detalhe"),

]
