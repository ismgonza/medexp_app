import os
import django
from decimal import Decimal

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Now that Django is set up, we can import our models
from django.db.models import Sum
from patients.models import Patient
from payments.models import Payment
from procedures.models import Procedure

def recalculate_balances():
    print("Starting balance recalculation...")
    
    for patient in Patient.objects.all():
        print(f"\nPatient {patient.id}: {patient.first_name} {patient.last_name1}")
        
        # Get all procedures
        procedures = Procedure.objects.filter(patient=patient)
        total_procedures = procedures.aggregate(total=Sum('total_cost'))['total'] or Decimal('0')
        
        print(f"Total Procedures: {total_procedures:.2f}")
        
        # Get all payments
        payments = Payment.objects.filter(patient=patient)
        
        print("Payments:")
        total_non_credit_payments = Decimal('0')
        total_credit_payments = Decimal('0')
        
        for payment in payments:
            print(f"  - Amount: {payment.amount:.2f}, Method: {payment.payment_method}, Is Credit: {payment.is_credit_payment}")
            if payment.payment_method == 'CREDIT' or payment.is_credit_payment:
                total_credit_payments += payment.amount
            else:
                total_non_credit_payments += payment.amount
        
        print(f"Total Non-Credit Payments: {total_non_credit_payments:.2f}")
        print(f"Total Credit Payments: {total_credit_payments:.2f}")
        
        # Calculate balance
        balance = total_non_credit_payments - total_procedures
        amount_in_favor = max(balance, Decimal('0'))
        
        print(f"Calculated Balance: {balance:.2f}")
        print(f"Amount in Favor: {amount_in_favor:.2f}")
        
        # Update patient balance
        patient.balance.amount_in_favor = amount_in_favor
        patient.balance.save()
        
        print("---")

    print("Balance recalculation completed.")

if __name__ == "__main__":
    recalculate_balances()