from django.db import models

class Padron(models.Model):
    id_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    lastname1 = models.CharField(max_length=100)
    lastname2 = models.CharField(max_length=100, blank=True)
    deceased = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.id_number} - {self.first_name} {self.lastname1} {self.lastname2}"

    class Meta:
        indexes = [
            models.Index(fields=['id_number']),
        ]
        verbose_name = "Padrón"
        verbose_name_plural = "Padrón"