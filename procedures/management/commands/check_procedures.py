from django.core.management.base import BaseCommand
from procedures.models import Procedure
from django.db.models import Count

class Command(BaseCommand):
    help = 'Check the number of procedures in the database and list them by payment status'

    def handle(self, *args, **options):
        procedure_count = Procedure.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Number of procedures: {procedure_count}'))
        
        payment_status_counts = Procedure.objects.values('payment_status').annotate(count=Count('id'))
        self.stdout.write(self.style.SUCCESS('Payment status counts:'))
        for status in payment_status_counts:
            self.stdout.write(f"{status['payment_status']}: {status['count']}")
            
        self.stdout.write(self.style.SUCCESS('\nDetailed list of procedures by payment status:'))
        for status in Procedure.PAYMENT_STATUS_CHOICES:
            procedures = Procedure.objects.filter(payment_status=status[0])
            self.stdout.write(self.style.SUCCESS(f"\n{status[1]} procedures:"))
            if procedures.exists():
                for procedure in procedures:
                    self.stdout.write(f"ID: {procedure.id}, Date: {procedure.procedure_date}, Patient: {procedure.patient}, Type: {procedure.procedure_type}")
            else:
                self.stdout.write("No procedures with this status")