from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Prefetch
from categorias.models import Categoria
from produtos.models import Produto
from produtos.serializers import ProdutoSerializer
from django.shortcuts import get_object_or_404
import json


class ProdutoListCreateView(ListCreateAPIView):
    """
    Listagem e criação de produtos no mesmo endpoint
    GET /produtos/list-create/  -> lista todos
    POST /produtos/list-create/ -> cria novo
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer


class ProdutoRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    Visualização, atualização e deleção em um único endpoint
    GET /produtos/<pk>/detail/     -> mostra detalhes
    PUT/PATCH /produtos/<pk>/detail/ -> atualiza
    DELETE /produtos/<pk>/detail/   -> deleta
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

# Views personalizadas com filtros
class ProdutoAtivosListView(ListAPIView):
    """
    Listagem apenas de produtos ativos
    GET /produtos/ativos/
    """
    serializer_class = ProdutoSerializer
    
    def get_queryset(self):
        return Produto.objects.filter(ativo=True)


class BaseCategoriaAPIView(APIView):
    categoria_nome = ""

    def get(self, request):
        categoria = get_object_or_404(Categoria, nome__iexact=self.categoria_nome)
        produtos = categoria.produtos.filter(ativo=True).order_by("codigo")

        if not produtos.exists():
            return Response(
                {"mensagem": "Nenhum produto encontrado nesta categoria."},
                status=status.HTTP_404_NOT_FOUND
            )

        produtos_lista = []
        produtos_formatados = []

        for produto in produtos:
            preco_formatado = f"R$ {produto.preco:.2f}".replace(".", ",")
            
            produto_dict = {
                "codigo": produto.codigo,
                "nome": produto.nome,
                "preco": produto.preco,
                "preco_formatado": preco_formatado,
                "descricao": produto.descricao,
                "ativo": produto.ativo,
            }
            produtos_lista.append(produto_dict)

            produto_formatado = (
                f"Código: {produto.codigo}\n"
                f"*{produto.nome}*\n"
                f"Preço: {preco_formatado}\n"
                f"Ingredientes: {produto.descricao}\n"
                f"-------------------"
            )
            produtos_formatados.append(produto_formatado)

        return Response(
            {
                "produtos": produtos_lista,
                "formatado": "\n\n".join(produtos_formatados),
            },
            status=status.HTTP_200_OK
        )

class LanchesAPIView(BaseCategoriaAPIView):
    categoria_nome = "Lanches"

class PorcoesAPIView(BaseCategoriaAPIView):
    categoria_nome = "Porções"

class AdicionaisAPIView(BaseCategoriaAPIView):
    categoria_nome = "Adicionais"

class BebidasAPIView(BaseCategoriaAPIView):
    categoria_nome = "Bebidas"


from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Produto
import json

class ProdutoDetalheAPIView(APIView):
    def get(self, request, codigo):
        try:
            produto = get_object_or_404(Produto, codigo=codigo, ativo=True)

            # Validate and retrieve the quantity, default to 1
            try:
                quantidade = int(request.query_params.get('quantidade', 1))
            except ValueError:
                return Response(
                    {"error": "Invalid quantity value. It must be an integer."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            valor_total = produto.preco * quantidade
            preco_unitario = f"R$ {produto.preco:.2f}".replace(".", ",")
            preco_total = f"R$ {valor_total:.2f}".replace(".", ",")
            codigo_quantidade = f"{quantidade}x{produto.codigo}"

            confirmacao = (
                f"[ {produto.codigo} ] - {codigo_quantidade} - {produto.nome}\n"
                f"Preço unitário: {preco_unitario}\n"
                f"Total: {preco_total}"
            )

            return Response(
                {
                    "codigo": codigo_quantidade,  # string
                    "confirmacao": confirmacao,   # string
                    "nome": produto.nome,         # string
                    "preco": preco_unitario,      # string
                    "total": preco_total,         # string
                    "produto_info": {            # Returning a dictionary instead of stringified JSON
                        "codigo": produto.codigo,  # Use codigo instead of id
                        "quantidade": quantidade,
                        "valor_unitario": float(produto.preco),
                        "valor_total": float(valor_total)
                    }
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},  # Return the error message for debugging
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
