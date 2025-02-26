from django.contrib import admin
from pedidos.models import Pedido, ItemPedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'status', 'valor_total', 'data_pedido', 'forma_pagamento', 'pagamento_confirmado')
    list_filter = ('status', 'forma_pagamento', 'pagamento_confirmado')
    search_fields = ('cliente__nome', 'id', 'codigo_transacao')
    ordering = ('-data_pedido',)
    readonly_fields = ('data_pedido', 'data_pagamento', 'valor_total')


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'produto', 'quantidade', 'preco_unitario', 'subtotal')
    search_fields = ('produto__nome', 'pedido__id')
    ordering = ('pedido',)
