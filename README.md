# Padron Import Process

## Overview
This process imports a large JSON file containing Padron (electoral roll) data into the Django application's database. It uses a streaming parser to efficiently handle large files without excessive memory usage.

## Prerequisites
- Django application with a `padron` app installed
- `ijson` library installed (`pip install ijson`)
- Large JSON file with Padron data (e.g., `cr_padron_20240809.json`)

## Model
The `Padron` model in `padron/models.py`:

```python
from django.db import models

class Padron(models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    lastname1 = models.CharField(max_length=100)
    lastname2 = models.CharField(max_length=100, blank=True)
    deceased = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['id_number']),
        ]
```

## Import Command
Located in `padron/management/commands/import_padron.py`, this command uses `ijson` to stream-parse the JSON file and bulk insert records into the database.

## Usage
1. Ensure the JSON file is in the Django project's root directory.
2. Run the command:
   ```
   docker exec -it medexp_app-backend-1 python manage.py import_padron cr_padron_20240809.json --settings=config.settings.production
   ```

## Process
1. The script opens the JSON file and starts parsing it in chunks.
2. It processes each entry, creating `Padron` objects.
3. Every 5000 entries, it performs a bulk insert into the database.
4. The script provides progress updates every 10000 processed entries.
5. After processing all entries, it reports the total number of records and import duration.

## Notes
- The `deceased` flag is set to `False` for all imported records by default.
- The import uses `ignore_conflicts=True`, skipping entries that conflict with existing records.
- The process is designed to be memory-efficient and can handle large files (400MB+).

## PadronSearchView
This view in `patients/views.py` allows searching the imported Padron data:

```python
class PadronSearchView(View):
    def get(self, request, id_number):
        try:
            padron_entry = Padron.objects.get(id_number=id_number)
            return JsonResponse({
                'found': True,
                'first_name': padron_entry.first_name,
                'lastname1': padron_entry.lastname1,
                'lastname2': padron_entry.lastname2,
            })
        except Padron.DoesNotExist:
            return JsonResponse({
                'found': False,
                'message': 'No se encontró un registro coincidente. Por favor ingrese los datos manualmente.'
            })
```

## Maintenance
- Regularly backup the database before running large imports.
- Monitor server resources during import for any performance issues.
- Consider scheduling regular imports if Padron data is updated frequently.