import json
from django.http import JsonResponse
from escpos.printer import Usb
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook_pedido(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            numero_pedido = data.get("numero_pedido", "0000")
            pushName = data.get("pushName", "Cliente")
            entrega_tipo = data.get("Entrega", "Retirada no Local")
            fechamento_total = data.get("fechamento_total", "0,00")
            observacao = data.get("observacao", "")
            troco = data.get("troco", "")

            # Configura a impressora (USB)
            p = Usb(0x04b8, 0x0e15)  # Altere os valores conforme o modelo Bematch 420

            # Layout do pedido
            p.set(align="center", text_type="B", width=2, height=2)
            p.text("N O V O   P E D I D O\n")
            p.text("==============================\n")

            p.set(align="left", text_type="B", width=1, height=1)
            p.text(f"Pedido: {numero_pedido}\n")
            p.text(f"Nome: {pushName}\n")

            if entrega_tipo == "Tele Entrega":
                endereco = data.get("endereco", "Não informado")
                bairro = data.get("bairro", "Não informado")
                complemento = data.get("complemento", "Não informado")
                taxa_entrega = data.get("taxa_entrega", "0,00")

                p.text(f"🏡 Endereço: {endereco}\n")
                p.text(f"Bairro: {bairro}\n")
                p.text(f"Complemento: {complemento}\n")
                p.text(f"🚛 Taxa de Entrega: R$ {taxa_entrega}\n")

            elif entrega_tipo == "Comer no Local":
                mesa = data.get("mesa", "Não informado")
                p.text("📍 Local: Comer no Local\n")
                p.text(f"🪑 Mesa: {mesa}\n")

            else:  # Retirada no Local
                p.text("📍 Local: Retirada no Local\n")

            p.text("==============================\n")
            p.set(align="center", text_type="B", width=2, height=2)
            p.text(f"TOTAL: R$ {fechamento_total}\n")
            p.set(align="left", text_type="B", width=1, height=1)
            p.text("==============================\n")

            if observacao:
                p.text(f"📄 Observação: {observacao}\n")

            if troco:
                p.text(f"💰 Troco: {troco}\n")

            if entrega_tipo == "Tele Entrega":
                p.text("🕐 Prazo de entrega: 40 min\n")
            elif entrega_tipo == "Comer no Local":
                p.text("🕐 Pedido será servido em breve!\n")
            else:
                p.text("🕐 Prazo médio para retirada: 20 min\n")

            p.text("\n\n")  # Pula linhas
            p.cut()  # Corta o papel

            return JsonResponse({"status": "success", "message": "Pedido impresso com sucesso!"})

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "JSON inválido"}, status=400)

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Erro ao imprimir: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Método não permitido"}, status=405)
