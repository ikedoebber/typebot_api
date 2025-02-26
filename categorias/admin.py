from django.contrib import admin
from categorias.models import Categoria
from produtos.models import Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ativa', 'destaque')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ('nome', 'slug')
    list_filter = ('ativa', 'destaque')