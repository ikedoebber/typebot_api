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



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from escpos.printer import Usb  # Importando a classe Usb da biblioteca python-escpos
import logging
import os

logger = logging.getLogger(__name__)

class WebhookPedidoView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            dados = request.data
            logger.info(f"Dados recebidos: {dados}")

            # Verifica se todos os campos obrigatórios estão presentes
            campos_obrigatorios = ['numero_pedido', 'data_formatada', 'pushName', 'Entrega', 'pedido', 'Total']
            for campo in campos_obrigatorios:
                if campo not in dados:
                    logger.error(f"Campo obrigatório faltando: {campo}")
                    return Response({
                        "status": "error",
                        "message": f"Campo obrigatório faltando: {campo}"
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Configuração da impressora USB (ajustar conforme o modelo da impressora)
            VENDOR_ID = 0x04b8  # Exemplo, ID do fabricante da impressora (verifique o seu)
            PRODUCT_ID = 0x0202  # Exemplo, ID do produto da impressora (verifique o seu)
            try:
                # Inicializar a impressora USB
                printer = Usb(VENDOR_ID, PRODUCT_ID)
                logger.info("Conectado à impressora USB")
            except Exception as e:
                logger.error(f"Erro ao conectar com a impressora: {str(e)}")
                return Response({
                    "status": "error",
                    "message": f"Erro de conexão com a impressora: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Cabeçalho
            printer.set(align='center', bold=True, double_height=True, double_width=True)
            printer.text("░N░O░V░O░\n░P░E░D░I░D░O░\n")
            printer.set(align='center', bold=True, double_height=False, double_width=False)
            printer.text("=============================\n")
            printer.text(f"{dados['data_formatada']}\n")
            printer.text(f"Pedido: {dados['numero_pedido']}\n")
            printer.text("=============================\n\n")

            # Dados do cliente
            printer.set(bold=True)
            printer.text("✅ DADOS DO CLIENTE\n")
            printer.set(bold=False)
            printer.text(f"Nome: {dados['pushName']}\n\n")

            # Detalhes de entrega
            printer.set(bold=True)
            printer.text("📍 Detalhes de Entrega\n")
            printer.set(bold=False)
            if dados['Entrega'].lower() == "comer no local":
                printer.text(f"Forma de Retirada: {dados['Entrega']}\n")
            else:
                printer.text(f"🏡 Endereço: {dados.get('endereco', 'N/A')}\n")
                printer.text(f"Bairro: {dados.get('bairro', 'N/A')}\n")
                printer.text(f"Complemento: {dados.get('complemento', 'N/A')}\n")
            printer.text("=============================\n")

            # Itens do pedido
            printer.set(bold=True)
            printer.text("SEU PEDIDO:\n")
            printer.set(bold=False)
            for i in range(1, 7):
                pedido = dados.get(f'pedido{i}', '')
                observacao = dados.get(f'observacao{i}', '')
                if pedido:
                    printer.text(f"{pedido}\n")
                    if observacao:
                        printer.text(f"Observação: {observacao}\n\n")

            # Rodapé com valor e observações
            printer.text("=============================\n")
            printer.set(bold=True)
            printer.text(f"👉 Subtotal: R$ {dados['Total']},00\n")
            taxa_entrega = dados.get('taxa_entrega', '0')
            printer.text(f"🛵 Entrega: R$ {taxa_entrega},00\n")
            fechamento_total = dados.get('fechamento_total', dados['Total'])
            printer.text(f"📃 Total: R$ {fechamento_total},00\n")
            printer.set(bold=False)
            printer.text("=============================\n")

            # Tipo de pagamento
            pagamento = dados.get('Pagamento', 'N/A')
            printer.text(f"💳 Tipo de Pagamento: {pagamento}\n")
            printer.text("=============================\n")

            # Observações e troco
            observacao = dados.get('observacao', '')
            troco = dados.get('troco', '')
            printer.text(f"📄 Observação: {observacao}\n")
            if troco:
                printer.text(f"Troco: {troco}\n")
            printer.text("=============================\n")

            # Prazo para entrega/retirada
            if dados['Entrega'].lower() == "comer no local":
                printer.text("🕐 Prazo médio para retirada: 20 min\n")
            else:
                printer.text("🕐 Prazo para entrega: 40 min\n")

            # Cortar papel
            printer.cut()

            return Response({
                "status": "success",
                "message": "Pedido impresso com sucesso!"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar pedido: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "message": f"Erro ao processar pedido: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
