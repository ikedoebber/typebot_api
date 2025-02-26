from django import forms
from categorias.models import Categoria
from mptt.forms import TreeNodeChoiceField


class CategoriaForm(forms.ModelForm):
    parent = TreeNodeChoiceField(queryset=Categoria.objects.all(), required=False, empty_label="Nenhuma (Categoria Raiz)")

    class Meta:
        model = Categoria
        fields = ['nome', 'descricao', 'imagem', 'ativa', 'destaque', 'ordem', 'parent', 'icone', 'cor', 'meta_title', 'meta_description']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagem': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'destaque': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-control'}),
            'icone': forms.TextInput(attrs={'class': 'form-control'}),
            'cor': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'meta_title': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
