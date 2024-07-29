import django_filters
from django.db.models import Q
from django import forms
from .models import Procedure

class ProcedureFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_fields', label="")
    payment_status = django_filters.MultipleChoiceFilter(
        choices=Procedure.PAYMENT_STATUS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Estado de Pago"
    )

    class Meta:
        model = Procedure
        fields = ['search', 'payment_status']

    def search_fields(self, queryset, name, value):
        return queryset.filter(
            Q(patient__first_name__icontains=value) |
            Q(patient__last_name1__icontains=value) |
            Q(patient__last_name2__icontains=value) |
            Q(patient__id_number__icontains=value) |
            Q(signed_by__first_name__icontains=value) |
            Q(signed_by__last_name__icontains=value)
        )
        
    def filter_include_paid(self, queryset, name, value):
        if not value:
            return queryset.exclude(payment_status='PAID')
        return queryset