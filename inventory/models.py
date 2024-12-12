from django.db import models
from django.core.validators import MinValueValidator

class InventoryItem(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Descripción del servicio o producto")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)]
        )
    active = models.BooleanField(default=True)
    variable_price = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code', 'name']
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        