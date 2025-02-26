from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from categorias.models import Categoria
from categorias.serializers import CategoriaSerializer
from produtos.models import Produto
from produtos.serializers import ProdutoSerializer


class CategoriaListView(generics.ListCreateAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_queryset(self):
        queryset = Categoria.objects.all()

        return self.filter_queryset(queryset)

    def filter_queryset(self, queryset):
        # Filtra apenas categorias ativas
        if self.request.query_params.get('ativas', None) == 'true':
            queryset = queryset.filter(ativa=True)

        # Filtra por destaque
        if self.request.query_params.get('destaque', None) == 'true':
            queryset = queryset.filter(destaque=True)

        return queryset


class CategoriaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    lookup_field = 'slug'


class CategoriaProdutosView(generics.GenericAPIView):
    serializer_class = ProdutoSerializer

    def get(self, request, slug=None):
        categoria = get_object_or_404(Categoria, slug=slug)
        produtos = Produto.objects.filter(categoria=categoria, ativo=True).order_by('ordem', 'nome')

        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reordenar_produtos(self, request, slug=None):
        categoria = get_object_or_404(Categoria, slug=slug)
        produtos_ordem = request.data.get('produtos_ordem', [])

        if not produtos_ordem:
            return Response({'error': 'Nenhuma ordem de produtos fornecida'}, status=status.HTTP_400_BAD_REQUEST)

        for ordem_data in produtos_ordem:
            produto_id = ordem_data.get('id')
            nova_ordem = ordem_data.get('ordem')

            if produto_id is None or nova_ordem is None:
                continue  # Ignore invalid data

            Produto.objects.filter(
                id=produto_id,
                categoria=categoria
            ).update(ordem=nova_ordem)

        return Response({'status': 'produtos reordenados'})
