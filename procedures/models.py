from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Procedure(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PAID', 'Pagado'),
        ('PARTIAL', 'Pendiente'),
        ('UNPAID', 'No Pagado'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pendiente'),
        ('CANCELED', 'Cancelado'),
        ('COMPLETED', 'Completado'),
    ]

    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='procedures')
    procedure_date = models.DateField(default=timezone.now, editable=False)
    procedure_type = models.CharField(max_length=100)
    dental_piece = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True)
    location = models.ForeignKey('locations.Location', on_delete=models.PROTECT, null=False, blank=False)
    inventory_item = models.ForeignKey('inventory.InventoryItem', on_delete=models.PROTECT, null=False, blank=False)
    item_count = models.IntegerField(default=1)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    initial_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='UNPAID')
    signed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=False, blank=False, related_name='signed_procedures')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    def save(self, *args, **kwargs):
        if self.inventory_item and self.item_count:
            self.initial_cost = self.inventory_item.price * self.item_count
            self.total_cost = max(self.initial_cost - self.discount, Decimal('0'))
        super().save(*args, **kwargs)

    @property
    def balance(self):
        total_paid = self.payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')
        return max(self.total_cost - total_paid, Decimal('0'))


    def update_payment_status(self):
        if self.balance == 0:
            self.payment_status = 'PAID'
        elif self.balance < self.total_cost:
            self.payment_status = 'PARTIAL'
        else:
            self.payment_status = 'UNPAID'
        self.save()

    def __str__(self):
        return f"Procedure for {self.patient} on {self.procedure_date} - {self.get_status_display()}"

    class Meta:
        ordering = ['-procedure_date']
