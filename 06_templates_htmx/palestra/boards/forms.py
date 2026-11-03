"""Form HTML delle bacheche."""
from django import forms

from .models import Board


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        # TODO (passo 4): i campi title e description
        fields = []
