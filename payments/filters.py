import django_filters
from django.db.models import Q
from .models import Payment
from patients.models import Patient
from django_filters.widgets import RangeWidget
from django.forms import CheckboxSelectMultiple

class PaymentFilter(django_filters.FilterSet):
    payment_date = django_filters.DateFromToRangeFilter(
        field_name='payment_date',
        widget=RangeWidget(attrs={
            'type': 'date',
            'placeholder': 'YYYY-MM-DD',
            'class': 'form-control'
        })
    )
    payment_method = django_filters.MultipleChoiceFilter(
        choices=Payment.PAYMENT_METHOD_CHOICES,
        widget=CheckboxSelectMultiple,
    )
    
    class Meta:
        model = Payment
        fields = ['payment_date', 'payment_method']
