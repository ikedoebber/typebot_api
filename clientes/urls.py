from django.urls import path
from clientes.views import ClienteListCreateView, ClienteRetrieveUpdateDestroyView


urlpatterns = [
    path('clientes/', ClienteListCreateView.as_view(), name='cliente-list-create'),
    path('clientes/<int:pk>/', ClienteRetrieveUpdateDestroyView.as_view(), name='cliente-detail'),
]
