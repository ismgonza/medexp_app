from django import forms
from .models import Location
from django.utils.translation import gettext_lazy as _

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'province', 'canton', 'district', 'address', 'phone', 'is_active']
        labels = {
            'name': _('Nombre'),
            'province': _('Provincia'),
            'canton': _('Cantón'),
            'district': _('Distrito'),
            'address': _('Dirección'),
            'phone': _('Teléfono'),
            'is_active': _('Activo'),
        }
        widgets = {
            'province': forms.Select(attrs={'id': 'provincia'}),
            'canton': forms.Select(attrs={'id': 'canton'}),
            'district': forms.Select(attrs={'id': 'distrito'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }