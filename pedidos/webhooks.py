import json
import logging
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Configuração do logger
logger = logging.getLogger(__name__)

# Definição de constantes (verifique se essas variáveis estão definidas corretamente)
PRINTNODE_URL = "https://api.printnode.com/printjobs"
HEADERS = {"Authorization": "Basic SEU_TOKEN_AQUI"}  # Substitua pelo seu token real
PRINTER_ID = "1"  # Substitua pelo ID da impressora correta

@csrf_exempt
def webhook_pedido(request):
    """Handle incoming order webhook and print receipt."""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)
    
    try:
        data = json.loads(request.body)
        logger.info(f"Received order webhook: {data.get('numero_pedido', 'unknown')}")

        # Extração segura de dados
        numero_pedido = data.get("numero_pedido", "0000")
        pushName = data.get("pushName", "Cliente")
        entrega_tipo = data.get("Entrega", "Retirada no Local")
        fechamento_total = data.get("fechamento_total", "0,00")
        observacao = data.get("observacao", "")
        troco = data.get("troco", "")

        # Construção do texto do pedido
        texto_pedido = "N O V O   P E D I D O\n"
        texto_pedido += "==============================\n"
        texto_pedido += f"Pedido: {numero_pedido}\n"
        texto_pedido += f"Nome: {pushName}\n"

        if entrega_tipo == "Tele Entrega":
            endereco = data.get("endereco", "Não informado")
            bairro = data.get("bairro", "Não informado")
            complemento = data.get("complemento", "Não informado")
            taxa_entrega = data.get("taxa_entrega", "0,00")

            texto_pedido += f"🏡 Endereço: {endereco}\n"
            texto_pedido += f"Bairro: {bairro}\n"
            texto_pedido += f"Complemento: {complemento}\n"
            texto_pedido += f"🚛 Taxa de Entrega: R$ {taxa_entrega}\n"
        
        elif entrega_tipo == "Comer no Local":
            mesa = data.get("mesa", "Não informado")
            texto_pedido += "📍 Local: Comer no Local\n"
            texto_pedido += f"🪑 Mesa: {mesa}\n"

        else:  # Retirada no Local
            texto_pedido += "📍 Local: Retirada no Local\n"

        texto_pedido += "==============================\n"
        texto_pedido += f"TOTAL: R$ {fechamento_total}\n"
        texto_pedido += "==============================\n"

        if observacao:
            texto_pedido += f"📄 Observação: {observacao}\n"
        
        if troco:
            texto_pedido += f"💰 Troco: {troco}\n"
        
        if entrega_tipo == "Tele Entrega":
            texto_pedido += "🕐 Prazo de entrega: 40 min\n"
        elif entrega_tipo == "Comer no Local":
            texto_pedido += "🕐 Pedido será servido em breve!\n"
        else:
            texto_pedido += "🕐 Prazo médio para retirada: 20 min\n"

        texto_pedido += "\n\n"

        # Payload para impressão
        payload = {
            "printer": {"id": int(PRINTER_ID) if PRINTER_ID.isdigit() else PRINTER_ID},
            "title": f"Pedido #{numero_pedido}",
            "contentType": "text/plain",
            "content": texto_pedido,
            "options": {"copies": 1}
        }

        # Enviar para PrintNode
        logger.info(f"Sending print job for order #{numero_pedido}")
        response = requests.post(PRINTNODE_URL, headers=HEADERS, json=payload)

        if response.status_code in (200, 201):
            logger.info(f"Successfully printed order #{numero_pedido}")
            return JsonResponse({
                "status": "success",
                "message": "Pedido impresso com sucesso!",
                "print_job_id": response.json().get("id")
            })
        else:
            error_message = f"PrintNode error: {response.status_code} - {response.text}"
            logger.error(error_message)
            return JsonResponse({
                "status": "error",
                "message": "Erro ao enviar para o PrintNode",
                "details": error_message
            }, status=500)

    except json.JSONDecodeError:
        logger.error("Invalid JSON received in webhook")
        return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

    except Exception as e:
        logger.exception(f"Unexpected error in webhook_pedido: {str(e)}")
        return JsonResponse({"status": "error", "message": f"Erro ao imprimir: {str(e)}"}, status=500)
