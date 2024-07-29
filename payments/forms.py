from django import forms
from .models import Payment
from decimal import Decimal

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['invoice_number', 'amount', 'payment_method']
        widgets = {
            'invoice_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'amount': 'Monto',
            'payment_method': 'Método de Pago',
            'invoice_number': 'Número de Factura',
        }

    def __init__(self, *args, **kwargs):
        self.patient = kwargs.pop('patient', None)
        super().__init__(*args, **kwargs)
        if self.patient:
            amount_in_favor = self.patient.balance.amount_in_favor if hasattr(self.patient, 'balance') else Decimal('0.00')
            self.fields['payment_method'].help_text = f"Seleccione <strong>Crédito</strong> para utilizar el balance disponible: <strong>₡{amount_in_favor}</strong>"


    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        payment_method = cleaned_data.get('payment_method')

        if payment_method == 'CREDIT':
            if self.patient:
                amount_in_favor = self.patient.balance.amount_in_favor if hasattr(self.patient, 'balance') else Decimal('0.00')
                if amount > amount_in_favor:
                    raise forms.ValidationError("El monto no debe exceder el balance disponible.")


        return cleaned_data