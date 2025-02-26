from django.contrib import admin
from clientes.models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'codigo', 'data_cadastro')
    search_fields = ('nome', 'email', 'telefone', 'codigo')
    list_filter = ('data_cadastro',)
    ordering = ('nome',)
    readonly_fields = ('data_cadastro',)
    list_per_page = 100
    fieldsets = (
        ("Informações Principais", {
            "fields": ("nome", "email", "telefone", "codigo")
        }),
        ("Documentos", {
            "fields": ("rg", "cpf")
        }),
        ("Endereço", {
            "fields": ("endereco", "bairro")
        }),
        ("Data de Cadastro", {
            "fields": ("data_cadastro",)
        }),
    )
