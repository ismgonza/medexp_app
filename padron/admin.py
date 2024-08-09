from django.contrib import admin
from .models import Padron

@admin.register(Padron)
class PadronAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'first_name', 'lastname1', 'lastname2', 'deceased')
    list_filter = ('deceased',)
    search_fields = ('id_number', 'first_name', 'lastname1', 'lastname2')
    list_per_page = 20

    actions = ['mark_as_deceased', 'mark_as_not_deceased']

    def mark_as_deceased(self, request, queryset):
        updated = queryset.update(deceased=True)
        self.message_user(request, f'{updated} entries marked as deceased.')
    mark_as_deceased.short_description = "Mark selected entries as deceased"

    def mark_as_not_deceased(self, request, queryset):
        updated = queryset.update(deceased=False)
        self.message_user(request, f'{updated} entries marked as not deceased.')
    mark_as_not_deceased.short_description = "Mark selected entries as not deceased"