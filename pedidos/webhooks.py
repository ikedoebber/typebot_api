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
