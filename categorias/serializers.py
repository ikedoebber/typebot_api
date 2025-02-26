from rest_framework import serializers
from categorias.models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    total_produtos = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = [
            'id', 'nome', 'slug', 'descricao', 'imagem', 'ativa',
            'destaque', 'ordem', 'parent', 'children', 'icone',
            'cor', 'total_produtos', 'meta_title', 'meta_description'
        ]

    def get_children(self, obj):
        children = obj.get_children()  # Método do django-mptt
        return CategoriaSerializer(children, many=True).data

    def get_total_produtos(self, obj):
        return obj.produtos.count() if hasattr(obj, 'produtos') else 0
