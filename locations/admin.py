# locations/admin.py
from django.contrib import admin
from .models import Location

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'canton', 'district', 'phone', 'is_active')
    list_filter = ('province', 'is_active')
    search_fields = ('name', 'province', 'canton', 'district')