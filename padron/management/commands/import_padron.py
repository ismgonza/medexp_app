import json
import time
from django.core.management.base import BaseCommand
from django.db import transaction
from padron.models import Padron
from django.conf import settings
import os
import ijson

class Command(BaseCommand):
    help = 'Import padron data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='Name of the JSON file to import')

    def handle(self, *args, **options):
        print("Starting import process")
        
        filename = options['filename']
        file_path = os.path.join(settings.BASE_DIR, filename)

        print(f"File path: {file_path}")

        if not os.path.exists(file_path):
            print(f'File not found: {file_path}')
            return

        print(f'Starting import from {file_path}')

        try:
            print("Opening file")
            with open(file_path, 'rb') as file:
                print("Starting to parse JSON data")
                parser = ijson.parse(file)
                
                to_create = []
                count = 0
                start_time = time.time()

                for prefix, event, value in parser:
                    if prefix == 'item' and event == 'start_map':
                        item = {}
                    elif prefix.startswith('item.') and event == 'string':
                        key = prefix.split('.')[1]
                        item[key] = value
                    elif prefix == 'item' and event == 'end_map':
                        to_create.append(Padron(
                            id_number=item['id_number'],
                            first_name=item['first_name'],
                            lastname1=item['lastname1'],
                            lastname2=item.get('lastname2', ''),
                            deceased=False
                        ))
                        count += 1
                        
                        if len(to_create) >= 5000:
                            print(f"Bulk creating {len(to_create)} entries (total processed: {count})")
                            Padron.objects.bulk_create(to_create, ignore_conflicts=True)
                            to_create = []

                        if count % 10000 == 0:
                            print(f"Processed {count} entries")

                if to_create:
                    print(f"Bulk creating final {len(to_create)} entries (total processed: {count})")
                    Padron.objects.bulk_create(to_create, ignore_conflicts=True)

                end_time = time.time()
                duration = end_time - start_time
                print(f'Import completed successfully in {duration:.2f} seconds. Processed {count} entries.')
                
                final_count = Padron.objects.count()
                print(f"Final count in Padron table: {final_count}")

        except Exception as e:
            print(f'Error during import: {str(e)}')
            import traceback
            print(traceback.format_exc())

        self.stdout.write(self.style.SUCCESS('Import process completed.'))