from django.urls import path
from pedidos.views import PedidoRetrieveUpdateDestroyView, PedidoListView, PedidoCreateView, AlterarStatusPedidoView, CriarPedidoAPIView
from pedidos.webhooks import WebhookPedidoESCPOSView, WebhookPedidoPrintNodeView


urlpatterns = [
    path('pedidos/create/', PedidoCreateView.as_view(), name='pedido-create'),
    path('pedidos/', PedidoListView.as_view(), name='pedido-list'),
    path('pedidos/<int:pk>/', PedidoRetrieveUpdateDestroyView.as_view(), name='pedido-detail-full'),
    path('pedidos/<int:pk>/alterar-status/', AlterarStatusPedidoView.as_view(), name='pedido-alterar-status'),

    path("api/pedidos/", CriarPedidoAPIView.as_view(), name="criar_pedido"),
    path('api/webhook/escpos/', WebhookPedidoESCPOSView.as_view(), name='webhook-escpos'),
    path('api/webhook/printnode/', WebhookPedidoPrintNodeView.as_view(), name='webhook-printnode'),
]
