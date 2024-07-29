from django.db import models, transaction
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Efectivo'),
        ('CARD', 'Tarjeta'),
        ('TRANSFER', 'Transferencia'),
        ('CREDIT', 'Crédito'),
        ('OTHER', 'Otro'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='CASH')
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    procedure = models.ForeignKey('procedures.Procedure', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_credit_payment = models.BooleanField(default=False)
    payment_date = models.DateField(auto_now_add=True)

    @transaction.atomic
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.procedure:
            self.procedure.update_payment_status()

    @property
    def overpayment_amount(self):
        if self.procedure:
            procedure_total_paid = self.procedure.payments.aggregate(models.Sum('amount'))['amount__sum'] or Decimal('0')
            overpayment = max(procedure_total_paid - self.procedure.total_cost, Decimal('0'))
            return min(self.amount, overpayment)
        return Decimal('0')

    def __str__(self):
        return f"Payment of {self.amount} for {self.procedure or 'Credit'} on {self.payment_date}"

    class Meta:
        ordering = ['-payment_date', '-id']

@receiver(post_save, sender=Payment)
def update_patient_balance(sender, instance, created, **kwargs):
    if created and not instance.is_credit_payment:
        overpayment = instance.overpayment_amount
        if overpayment > 0:
            instance.patient.balance.increase_balance(overpayment, payment=instance)