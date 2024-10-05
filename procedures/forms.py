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
    )
    inventory_item = forms.ModelChoiceField(
        queryset=InventoryItem.objects.filter(active=True),
        empty_label="Seleccione",
        label=_('Tipo de Tratamiento'),
        required=False
    )
    item_count = forms.IntegerField(
        min_value=1,
        initial=1,
        label=_('Cantidad'),
        required=False
    )
    discount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        initial=0,
        label=_('Descuento'),
        required=False
    )
    signed_by = forms.ModelChoiceField(
        queryset=get_user_model().objects.none(),
        empty_label="Seleccione",
        label=_('Dr(a) Responsable')
    )
    procedure_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date(),
        label=_('Fecha del Procedimiento')
    )
    initial_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        label=_('SubTotal')
    )
    unit_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label=_('Precio por Unidad')
    )

    class Meta:
        model = Procedure
        fields = ['patient', 'location', 'procedure_type', 'inventory_item', 'initial_cost', 'item_count', 'dental_piece', 'notes', 'discount', 'total_cost', 'signed_by', 'procedure_date', 'unit_price']
        labels = {
            'location': _('Sucursal'),
            'procedure_type': _('Tipo de Tratamiento'),
            'dental_piece': _('Piezas Dentales'),
            'notes': _('Notas'),
            'item_count': _('Cantidad'),
            'total_cost': _('Costo Total'),
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

        if self.instance.pk and self.instance.inventory_item:
            self.fields['unit_price'].initial = self.instance.unit_price or self.instance.inventory_item.price
            if not self.instance.inventory_item.variable_price:
                self.fields['unit_price'].widget.attrs['readonly'] = True
            
            # Add this block to set the initial value for procedure_type
            self.fields['procedure_type'].initial = self.instance.procedure_type
            self.fields['inventory_item'].initial = self.instance.inventory_item

    def clean(self):
        cleaned_data = super().clean()
        inventory_item = cleaned_data.get('inventory_item')
        unit_price = cleaned_data.get('unit_price')

        if inventory_item and not inventory_item.variable_price:
            cleaned_data['unit_price'] = inventory_item.price

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.inventory_item and instance.item_count:
            if instance.inventory_item.variable_price:
                unit_price = self.cleaned_data.get('unit_price', instance.inventory_item.price)
            else:
                unit_price = instance.inventory_item.price
            instance.unit_price = unit_price
            instance.initial_cost = unit_price * instance.item_count
            instance.total_cost = max(instance.initial_cost - instance.discount, Decimal('0'))
        if commit:
            instance.save()
        return instance