"""Forms per boards."""
from django import forms
from .models import Board


class BoardForm(forms.ModelForm):
    """
    Form per creare/modificare una board.
    TODO: Aggiungi validazione custom per title (min 3 caratteri).
    """
    class Meta:
        model = Board
        fields = ['title', 'description']
        # TODO: Aggiungi widgets con classi CSS per stile
        # widgets = {
        #     'title': forms.TextInput(attrs={'class': 'form-control'}),
        #     'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        # }
    
    # TODO: Aggiungi clean_title per validazione
    # def clean_title(self):
    #     title = self.cleaned_data.get('title')
    #     if len(title) < 3:
    #         raise forms.ValidationError('Il titolo deve avere almeno 3 caratteri')
    #     return title
