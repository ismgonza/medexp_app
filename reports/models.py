from django.db import models

class Report(models.Model):
    # You don't need to add any fields here if you're not storing report data
    class Meta:
        managed = False  # This tells Django not to create a database table for this model
        permissions = [
            ("view_reports", "Can view reports"),
        ]