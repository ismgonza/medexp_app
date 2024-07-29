from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['code', 'name', 'description', 'price', 'active']
        labels = {
            'code': 'Código',
            'name': 'Nombre',
            'description': 'Descripción',
            'price': 'Precio',
            'active': 'Activo',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }