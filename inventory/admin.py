from django.contrib import admin
from .models import InventoryItem

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'price')
    list_filter = ('price',)
    search_fields = ('code', 'name', 'description')
    ordering = ('code', 'name')