import json
from django.core.management.base import BaseCommand
from django.db import transaction
from padron.models import Padron
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Import padron data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the JSON file to import')

    def handle(self, *args, **options):
        filename = options['filename']
        file_path = os.path.join(settings.BASE_DIR, filename)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Starting import from {file_path}'))

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            with transaction.atomic():
                # Create a set of all existing id_numbers
                existing_ids = set(Padron.objects.values_list('id_number', flat=True))

                # Prepare bulk create and update lists
                to_create = []
                to_update = []

                for item in data:
                    if item['id_number'] in existing_ids:
                        to_update.append(Padron(
                            id_number=item['id_number'],
                            first_name=item['first_name'],
                            lastname1=item['lastname1'],
                            lastname2=item['lastname2'],
                            # Keep existing 'deceased' status for updates
                        ))
                    else:
                        to_create.append(Padron(
                            id_number=item['id_number'],
                            first_name=item['first_name'],
                            lastname1=item['lastname1'],
                            lastname2=item['lastname2'],
                            deceased=False  # New entries are not deceased by default
                        ))

                # Bulk create new entries
                Padron.objects.bulk_create(to_create)

                # Bulk update existing entries
                Padron.objects.bulk_update(to_update, ['first_name', 'lastname1', 'lastname2'])

            self.stdout.write(self.style.SUCCESS(f'Import completed successfully. Created {len(to_create)} new entries and updated {len(to_update)} existing entries.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during import: {str(e)}'))