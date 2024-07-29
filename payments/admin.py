from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('procedure_id', 'amount', 'payment_date')
    list_filter = ('payment_date',)
    search_fields = ('procedure__patient__first_name', 'procedure__patient__last_name1', 'procedure__patient__last_name2')
    date_hierarchy = 'payment_date'