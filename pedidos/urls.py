from django.urls import path
from pedidos import webhooks
from pedidos.views import PedidoRetrieveUpdateDestroyView, PedidoListView, PedidoCreateView, AlterarStatusPedidoView, CriarPedidoAPIView


urlpatterns = [
    path('pedidos/create/', PedidoCreateView.as_view(), name='pedido-create'),
    path('pedidos/', PedidoListView.as_view(), name='pedido-list'),
    path('pedidos/<int:pk>/', PedidoRetrieveUpdateDestroyView.as_view(), name='pedido-detail-full'),
    path('pedidos/<int:pk>/alterar-status/', AlterarStatusPedidoView.as_view(), name='pedido-alterar-status'),

    path("api/pedidos/", CriarPedidoAPIView.as_view(), name="criar_pedido"),
    path('webhook/pedido/', WebhookPedidoView.as_view(), name='webhook_pedido'),
]
