from django.db import models
from categorias.models import Categoria


class Produto(models.Model):
    codigo = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()
    categoria = models.ForeignKey('categorias.Categoria', related_name='produtos', on_delete=models.PROTECT)
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='produtos/', null=True, blank=True)

    def __str__(self):
        return self.nome

