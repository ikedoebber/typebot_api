from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from escpos.printer import Usb
import logging
import requests
import json
import os
from datetime import datetime
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)

class WebhookPedidoESCPOSView(APIView):
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

            # Imprimir o cupom baseado no tipo de entrega
            if dados['Entrega'].lower() == "comer no local":
                self._imprimir_cupom_local(printer, dados)
            else:
                self._imprimir_cupom_entrega(printer, dados)

            # Cortar papel
            printer.cut()
            printer.close()

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
    
    def _imprimir_cupom_local(self, printer, dados):
        """Imprime o cupom para cliente que vai comer no local"""
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
        printer.text(f"Forma de Retirada: {dados['Entrega']}\n")
        printer.text("=============================\n")

        # Itens do pedido
        printer.set(bold=True)
        printer.text("SEU PEDIDO:\n")
        printer.set(bold=False)
        self._imprimir_itens_pedido(printer, dados)

        # Rodapé
        printer.text("=============================\n")
        printer.set(bold=True)
        printer.text(f"📃 Total: R$ {dados.get('fechamento_total', dados['Total'])},00\n")
        printer.set(bold=False)
        printer.text("=============================\n")

        # Observações
        observacao = dados.get('observacao', '')
        troco = dados.get('troco', '')
        printer.text(f"📄 Observação: {observacao}\n")
        if troco:
            printer.text(f"Troco: {troco}\n")
        printer.text("=============================\n")
        printer.text("🕐 Prazo médio para retirada: 20 min\n")

    def _imprimir_cupom_entrega(self, printer, dados):
        """Imprime o cupom para entrega"""
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
        printer.text(f"🏡 Endereço: {dados.get('endereco', 'N/A')}\n")
        printer.text(f"Bairro: {dados.get('bairro', 'N/A')}\n")
        printer.text(f"Complemento: {dados.get('complemento', 'N/A')}\n")
        printer.text("=============================\n")

        # Itens do pedido
        printer.set(bold=True)
        printer.text("SEU PEDIDO:\n")
        printer.set(bold=False)
        self._imprimir_itens_pedido(printer, dados)

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
        printer.text("🕐 Prazo para entrega: 40 min\n")

    def _imprimir_itens_pedido(self, printer, dados):
        """Imprime os itens do pedido"""
        # Item principal
        if 'pedido' in dados and dados['pedido']:
            printer.text(f"{dados['pedido']}\n")
        
        # Itens adicionais (1-6)
        for i in range(1, 7):
            pedido = dados.get(f'pedido{i}', '')
            observacao = dados.get(f'observacao{i}', '')
            if pedido:
                printer.text(f"{pedido}\n")
                if observacao:
                    printer.text(f"Observação: {observacao}\n\n")


logger = logging.getLogger(__name__)

class WebhookPedidoPrintNodeView(APIView):
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

            # Prepara os itens do pedido para o template
            itens_pedido = []
            # Adiciona o item principal se existir
            if 'pedido' in dados and dados['pedido']:
                itens_pedido.append({
                    'nome': dados['pedido'],
                    'observacao': ''
                })
            
            # Adiciona os itens adicionais
            for i in range(1, 7):
                pedido = dados.get(f'pedido{i}', '')
                observacao = dados.get(f'observacao{i}', '')
                if pedido:
                    itens_pedido.append({
                        'nome': pedido,
                        'observacao': observacao
                    })

            # Define qual template usar baseado no tipo de entrega
            template_name = 'templates/pedido_local.html' if dados['Entrega'].lower() == "comer no local" else 'templates/pedido_entrega.html'
            
            # Render do HTML baseado no template
            contexto = {
                'dados': dados,
                'itens_pedido': itens_pedido,
                'data_impressao': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            }
            
            conteudo_html = render_to_string(template_name, contexto)
            
            # Configuração do PrintNode
            PRINTNODE_API_KEY = "eyOfX__SFjNOt52yqAL5o7pMi5bpghIYF5muhZql0kM"  # Obtenha sua chave da API PrintNode
            PRINTER_ID = os.environ.get('PRINTNODE_PRINTER_ID')  # ID da impressora no PrintNode
            
            if not PRINTNODE_API_KEY or not PRINTER_ID:
                logger.error("Configurações do PrintNode não definidas")
                return Response({
                    "status": "error",
                    "message": "Configurações do PrintNode não definidas"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Cria o job de impressão no PrintNode
            url = f"https://api.printnode.com/printjobs"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {PRINTNODE_API_KEY}"
            }
            
            payload = {
                "printerId": int(PRINTER_ID),
                "title": f"Pedido #{dados['numero_pedido']}",
                "contentType": "html",
                "content": conteudo_html,
                "source": "RestAPI"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 201:
                logger.error(f"Erro ao enviar para PrintNode: {response.text}")
                return Response({
                    "status": "error",
                    "message": f"Erro ao enviar para PrintNode: {response.text}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info(f"Pedido enviado para PrintNode com sucesso: {response.json()}")
            
            return Response({
                "status": "success",
                "message": "Pedido enviado para impressão com sucesso!",
                "job_id": response.json()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Erro ao processar pedido: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "message": f"Erro ao processar pedido: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
