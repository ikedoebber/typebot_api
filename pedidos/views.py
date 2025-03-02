from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from pedidos.models import Pedido, ItemPedido
from pedidos.serializers import PedidoSerializer
from clientes.models import Cliente
from produtos.models import Produto



class PedidoCreateView(CreateAPIView):
    """
    Apenas criação de pedidos
    POST /pedidos/create/
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

class PedidoListView(ListAPIView):
    """
    Apenas listagem de pedidos
    GET /pedidos/
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class PedidoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Visualização, atualização e deleção em um único endpoint
    GET /pedidos/<pk>/
    PUT/PATCH /pedidos/<pk>/
    DELETE /pedidos/<pk>/
    """
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer


class AlterarStatusPedidoView(APIView):
    """
    Altera o status de um pedido específico
    POST /pedidos/<pk>/alterar-status/
    
    Exemplo de payload:
    {
        "status": "novo_status"
    }
    """
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        novo_status = request.data.get('status')
        
        if novo_status in [choice[0] for choice in Pedido.STATUS_CHOICES]:
            pedido.status = novo_status
            pedido.save()
            return Response({'status': 'status atualizado'})
        return Response(
            {'erro': 'status inválido'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class CriarPedidoAPIView(APIView):
    def post(self, request):
        cliente_id = request.data.get("cliente")
        itens = request.data.get("itens")  # Deve ser uma lista de dicionários

        if not cliente_id or not itens:
            return Response({"erro": "Cliente e itens são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        cliente = get_object_or_404(Cliente, id=cliente_id)
        pedido = Pedido.objects.create(cliente=cliente, subtotal=0)

        subtotal = 0

        for item in itens:
            codigo = item.get("codigo")
            quantidade = item.get("quantidade", 1)

            produto = get_object_or_404(Produto, codigo=codigo)
            preco_unitario = produto.preco
            subtotal_item = quantidade * preco_unitario

            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                subtotal=subtotal_item
            )

            subtotal += subtotal_item

        # Atualiza subtotal e total do pedido
        pedido.subtotal = subtotal
        pedido.save()

        return Response({"mensagem": "Pedido salvo com sucesso!", "pedido_id": pedido.id}, status=status.HTTP_201_CREATED)
