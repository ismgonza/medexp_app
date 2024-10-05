from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['code', 'name', 'description', 'price', 'active', 'variable_price']
        labels = {
            'code': 'Código',
            'name': 'Nombre',
            'description': 'Descripción',
            'price': 'Precio',
            'active': 'Activo',
            'variable_price': 'Precio Variable',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }