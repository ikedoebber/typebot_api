from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('em_preparo', 'Em Preparo'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado')
    ]

    TIPO_ENTREGA_CHOICES = [
        ('retirada', 'Retirada no Local'),
        ('delivery', 'Delivery'),
        ('comer no local', 'Comer no local')
    ]

    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro'),
        ('pix', 'PIX'),
        ('cartao_credito', 'Cartão de Crédito'),
        ('cartao_debito', 'Cartão de Débito'),
    ]

    # Campos básicos
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    data_pedido = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    observacoes = models.TextField(blank=True, null=True)

    # Campos de valores
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taxa_entrega = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    # Campos de entrega
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA_CHOICES, default='retirada')
    endereco_entrega = models.TextField(blank=True, null=True)
    cep_entrega = models.CharField(max_length=9, blank=True, null=True)
    previsao_entrega = models.DateTimeField(null=True, blank=True)

    # Campos de pagamento
    forma_pagamento = models.CharField(max_length=20, choices=FORMA_PAGAMENTO_CHOICES)
    pagamento_confirmado = models.BooleanField(default=False)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    codigo_transacao = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-data_pedido']
        indexes = [
            models.Index(fields=['-data_pedido']),
            models.Index(fields=['status']),
            models.Index(fields=['cliente']),
        ]

    def save(self, *args, **kwargs):
        # Calcula o valor total
        self.valor_total = self.subtotal - self.desconto + self.taxa_entrega
        
        # Atualiza o histórico de status
        if not self._state.adding:  # Se não é uma nova instância
            old_instance = Pedido.objects.get(pk=self.pk)
            if old_instance.status != self.status:
                if not isinstance(self.historico_status, list):
                    self.historico_status = []
                self.historico_status.append({
                    'de': old_instance.status,
                    'para': self.status,
                    'data': timezone.now().isoformat()
                })
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente.nome}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey('produtos.Produto', on_delete=models.PROTECT)
    quantidade = models.IntegerField(validators=[MinValueValidator(1)])
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    desconto_item = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacoes_item = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['pedido', 'produto']),
        ]

    def save(self, *args, **kwargs):
        self.subtotal = (self.quantidade * self.preco_unitario) - self.desconto_item
        super().save(*args, **kwargs)
        
        # Atualiza o subtotal do pedido
        self.pedido.subtotal = sum(item.subtotal for item in self.pedido.itens.all())
        self.pedido.save()

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
