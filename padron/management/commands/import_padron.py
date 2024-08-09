import json
import time
import logging
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
        # Set up logging
        logging.basicConfig(filename='/tmp/padron_import.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logger = logging.getLogger(__name__)

        filename = options['filename']
        file_path = os.path.join(settings.BASE_DIR, filename)

        if not os.path.exists(file_path):
            logger.error(f'File not found: {file_path}')
            return

        logger.info(f'Starting import from {file_path}')

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            logger.info(f"Loaded {len(data)} entries from JSON file")

            start_time = time.time()
            with transaction.atomic():
                existing_ids = set(Padron.objects.values_list('id_number', flat=True))
                logger.info(f"Found {len(existing_ids)} existing entries in database")

                to_create = []
                to_update = []

                for i, item in enumerate(data, 1):
                    if item['id_number'] in existing_ids:
                        to_update.append(Padron(
                            id_number=item['id_number'],
                            first_name=item['first_name'],
                            lastname1=item['lastname1'],
                            lastname2=item['lastname2'],
                        ))
                    else:
                        to_create.append(Padron(
                            id_number=item['id_number'],
                            first_name=item['first_name'],
                            lastname1=item['lastname1'],
                            lastname2=item['lastname2'],
                            deceased=False
                        ))

                    if i % 10000 == 0:
                        logger.info(f"Processed {i}/{len(data)} entries")

                logger.info(f"Creating {len(to_create)} new entries")
                Padron.objects.bulk_create(to_create, batch_size=5000)

                logger.info(f"Updating {len(to_update)} existing entries")
                Padron.objects.bulk_update(to_update, ['first_name', 'lastname1', 'lastname2'], batch_size=5000)

            end_time = time.time()
            duration = end_time - start_time
            logger.info(f'Import completed successfully in {duration:.2f} seconds. Created {len(to_create)} new entries and updated {len(to_update)} existing entries.')
            
            final_count = Padron.objects.count()
            logger.info(f"Final count in Padron table: {final_count}")

        except Exception as e:
            logger.error(f'Error during import: {str(e)}', exc_info=True)

        self.stdout.write(self.style.SUCCESS('Import process completed. Check /tmp/padron_import.log for details.'))