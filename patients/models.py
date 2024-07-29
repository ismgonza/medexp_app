from django.db import models, transaction
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.db.models import Sum


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    MARITAL_STATUS_CHOICES = [
        ('S', 'Soltero(a)'),
        ('C', 'Casado(a)'),
        ('D', 'Divorciado(a)'),
        ('V', 'Viudo(a)'),
    ]
    REFERRAL_CHOICES = [
        ('internet', 'Búsqueda en Internet'),
        ('social_media', 'Redes sociales'),
        ('recommendation', 'Recomendación de un amigo o familiar'),
        ('online_ad', 'Publicidad en línea'),
        ('outdoor_ad', 'Publicidad exterior'),
    ]

    # Personal Information
    id_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField()
    first_name = models.CharField(max_length=100)
    last_name1 = models.CharField(max_length=100)
    last_name2 = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS_CHOICES)

    # Contact Information
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?\d{8,15}$', message="Phone number must be entered in the format: '+50612345678' or '+15061234567'. Up to 15 digits allowed.")
    primary_phone = models.CharField(validators=[phone_regex], max_length=17)
    work_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Address
    province = models.CharField(max_length=100)
    canton = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    address_details = models.TextField()

    # Emergency Contacts
    emergency_contact1 = models.CharField(max_length=100)
    emergency_phone1 = models.CharField(validators=[phone_regex], max_length=17)
    emergency_contact2 = models.CharField(max_length=100, blank=True)
    emergency_phone2 = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    # Additional Data
    admission_date = models.DateField(default=timezone.now)
    referral_source = models.CharField(max_length=20, choices=REFERRAL_CHOICES)
    consultation_reason = models.TextField()
    receive_notifications = models.BooleanField(default=False)

    # Medical History
    under_treatment = models.BooleanField()
    under_treatment_text = models.CharField(max_length=100, blank=True)
    current_medication = models.BooleanField()
    current_medication_text = models.CharField(max_length=100, blank=True)
    serious_illnesses = models.BooleanField()
    serious_illnesses_text = models.CharField(max_length=100, blank=True)
    surgeries = models.BooleanField()
    surgeries_text = models.CharField(max_length=100, blank=True)
    allergies = models.BooleanField()
    allergies_text = models.CharField(max_length=100, blank=True)
    anesthesia_issues = models.BooleanField()
    bleeding_issues = models.BooleanField()
    pregnant_or_lactating = models.BooleanField()
    contraceptives = models.BooleanField()

    # Medical Conditions
    high_blood_pressure = models.BooleanField()
    rheumatic_fever = models.BooleanField()
    drug_addiction = models.BooleanField()
    diabetes = models.BooleanField()
    anemia = models.BooleanField()
    thyroid = models.BooleanField()
    asthma = models.BooleanField()
    arthritis = models.BooleanField()
    cancer = models.BooleanField()
    heart_problems = models.BooleanField()
    smoker = models.BooleanField()
    ulcers = models.BooleanField()
    gastritis = models.BooleanField()
    hepatitis = models.BooleanField()
    kidney_diseases = models.BooleanField()
    hormonal_problems = models.BooleanField()
    epilepsy = models.BooleanField()
    aids = models.BooleanField()
    psychiatric_treatment = models.BooleanField()

    # Confirmation
    information_confirmed = models.BooleanField(null=False, blank=False)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.upper()
        self.last_name1 = self.last_name1.upper()
        self.last_name2 = self.last_name2.upper()
        super(Patient, self).save(*args, **kwargs)
        
        if 'request' in kwargs:
            request = kwargs.pop('request')
            if not self.pk:
                self.created_by = request.user
            self.updated_by = request.user
        super(Patient, self).save(*args, **kwargs)


    def __str__(self):
        return f"{self.first_name} {self.last_name1} {self.last_name2}"

    class Meta:
        ordering = ['last_name1', 'last_name2', 'first_name']
        
class PatientBalance(models.Model):
    patient = models.OneToOneField('Patient', on_delete=models.CASCADE, related_name='balance')
    amount_in_favor = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)

    def increase_balance(self, amount, payment=None):
        with transaction.atomic():
            if amount < 0:
                raise ValidationError("Amount must be positive")
            self.amount_in_favor += amount
            self.save()
            CreditTransaction.objects.create(
                patient_balance=self,
                amount=amount,
                transaction_type='INCREASE',
                payment=payment
            )

    def decrease_balance(self, amount, payment=None):
        with transaction.atomic():
            if amount < 0:
                raise ValidationError("Amount must be positive")
            if amount > self.amount_in_favor:
                raise ValidationError("Not enough balance available")
            self.amount_in_favor -= amount
            self.save()
            CreditTransaction.objects.create(
                patient_balance=self,
                amount=amount,
                transaction_type='DECREASE',
                payment=payment
            )

    def apply_to_procedure(self, procedure, amount):
        from payments.models import Payment
        with transaction.atomic():
            if amount < 0:
                raise ValidationError("Amount must be positive")
            if amount > self.amount_in_favor:
                raise ValidationError("Not enough balance available")
            if amount > procedure.balance:
                raise ValidationError("Amount exceeds procedure balance")
            
            self.decrease_balance(amount, procedure)
            payment = Payment.objects.create(
                procedure=procedure,
                patient=self.patient,
                amount=amount,
                payment_method='CREDIT',
                is_credit_payment=True
            )
            procedure.update_payment_status()
            return payment

    def __str__(self):
        return f"Balance for {self.patient}: {self.amount_in_favor}"
    
    def recalculate_balance(self):
        with transaction.atomic():
            # Calculate total non-credit payments
            total_payments = self.patient.payments.filter(
                is_credit_payment=False,
                payment_method__ne='CREDIT'
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

            # Calculate total procedure costs
            total_procedures = self.patient.procedures.aggregate(Sum('total_cost'))['total_cost__sum'] or Decimal('0.00')

            # Calculate new balance
            new_balance = max(total_payments - total_procedures, Decimal('0.00'))

            # Update the balance
            self.amount_in_favor = new_balance
            self.save()

            # Create a CreditTransaction for auditing purposes
            CreditTransaction.objects.create(
                patient_balance=self,
                amount=new_balance,
                transaction_type='RECALCULATE',
            )

        return new_balance
    
class CreditTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('INCREASE', 'Increase'),
        ('DECREASE', 'Decrease'),
    ]
    patient_balance = models.ForeignKey(PatientBalance, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} of {self.amount} for {self.patient_balance.patient}"