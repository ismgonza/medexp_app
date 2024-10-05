from django import forms
from .models import Procedure
from django.contrib.auth import get_user_model
from patients.models import Patient
from locations.models import Location
from inventory.models import InventoryItem
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.utils import timezone


class ProcedureForm(forms.ModelForm):
    location = forms.ModelChoiceField(
        queryset=Location.objects.filter(is_active=True),
        empty_label="Seleccione",
        label=_('Sucursal')
        ),
    inventory_item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(active=True),
        empty_label="Seleccione",
        label=_('Tipo de Tratamiento'),
        required=False
        ),
    item_count = forms.IntegerField(
        min_value=1,
        initial=1,
        label=_('Cantidad'),
        required=False
        ),
    discount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        initial=0,
        label=_('Descuento'),
        required=False
        ),
    signed_by = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),  # We'll set this in __init__
        empty_label="Seleccione",
        label=_('Dr(a) Responsable')
        ),
    procedure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        label=_('Fecha del Procedimiento')
        ),
    initial_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        label=_('SubTotal')
        )


    class Meta:
        model = Procedure
        fields = ['patient', 'location', 'procedure_type', 'inventory_item', 'initial_cost', 'item_count', 'dental_piece', 'notes', 'discount', 'total_cost', 'signed_by', 'procedure_date']

        labels = {
            'location': _('Sucursal'),
            'procedure_type': _('Tipo de Tratamiento'),
            'dental_piece': _('Piezas Dentales'),
            'notes': _('Notas'),
            'item_count': _('Cantidad'),
            'total_cost': _('Costo por Unidad'),
            'discount': _('Descuento'),
            'signed_by': _('Responsable'),
            'procedure_date': _('Fecha del Procedimiento'),
        }
        widgets = {
            'procedure_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'dental_piece': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set the queryset for signed_by to exclude superadmin users
        self.fields['signed_by'].queryset = get_user_model().objects.filter(
            is_active=True
        ).exclude(
            groups__name='superadmin'
        )
        
        if 'initial' in kwargs and 'patient' in kwargs['initial']:
            self.fields['patient'].initial = kwargs['initial']['patient']
            self.fields['total_cost'].widget.attrs['readonly'] = True
            self.fields['initial_cost'].widget.attrs['readonly'] = True
            self.fields['patient'].widget = forms.HiddenInput()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.inventory_item and instance.item_count:
            subtotal = instance.inventory_item.price * instance.item_count
            instance.total_cost = max(subtotal - instance.discount, Decimal('0'))
        if commit:
            instance.save()
        return instance
