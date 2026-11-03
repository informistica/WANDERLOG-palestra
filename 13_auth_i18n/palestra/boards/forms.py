"""Form HTML delle bacheche."""
from django import forms

from .models import Board


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description']
        # TODO (passo 6): rendi traducibile il testo con gettext_lazy
        help_texts = {'title': 'Per esempio: Weekend a Roma'}
