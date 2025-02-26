from django.contrib import admin
from produtos.models import Produto

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'preco', 'estoque', 'categoria', 'ativo')
    search_fields = ('codigo', 'nome', 'descricao')
    list_filter = ('categoria', 'ativo')
    ordering = ('codigo',)
    list_per_page = 100
    
    fieldsets = (
        (None, {
            'fields': ('codigo', 'nome', 'descricao', 'preco', 'estoque', 'categoria', 'ativo', 'imagem')
        }),
    )

admin.site.register(Produto, ProdutoAdmin)
