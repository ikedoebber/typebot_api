from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey

class Categoria(MPTTModel):
    nome = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    descricao = models.TextField(blank=True, null=True)
    imagem = models.ImageField(upload_to='categorias/', blank=True, null=True)
    ativa = models.BooleanField(default=True)
    destaque = models.BooleanField(default=False)
    ordem = models.IntegerField(default=0)
    parent = TreeForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    icone = models.CharField(max_length=50, blank=True, null=True)  # Ícones FontAwesome ou similares
    cor = models.CharField(max_length=7, default='#000000')  # Identificação visual
    meta_title = models.CharField(max_length=100, blank=True, null=True)  # SEO
    meta_description = models.TextField(blank=True, null=True)  # SEO

    class MPTTMeta:
        order_insertion_by = ['ordem', 'nome']

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug or Categoria.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = slugify(self.nome)
            while Categoria.objects.filter(slug=self.slug).exists():
                self.slug = f"{self.slug}-{Categoria.objects.count()}"
        super().save(*args, **kwargs)

    @property
    def produtos_ativos(self):
        return self.produtos.filter(ativo=True) if hasattr(self, 'produtos') else None

    @property
    def total_produtos(self):
        return self.produtos.count() if hasattr(self, 'produtos') else 0
