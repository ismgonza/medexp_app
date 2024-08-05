from django.contrib import admin
from django.template.response import TemplateResponse
from .models import Procedure
from django.utils.safestring import mark_safe

@admin.register(Procedure)
class ProcedureAdmin(admin.ModelAdmin):
    list_display = ('patient', 'procedure_date', 'procedure_type', 'total_cost', 'payment_status', 'signed_by')
    history_list_display = ['created_by', 'updated_by']
    search_fields = ('patient__first_name', 'patient__last_name1', 'patient__last_name2', 'procedure_type')
    readonly_fields = ('procedure_date', 'signed_by')
    list_filter = ('procedure_date', 'payment_status', 'signed_by')
    date_hierarchy = 'procedure_date'

    fieldsets = (
        ('Procedure Information', {
            'fields': ('patient', 'procedure_date', 'procedure_type', 'notes', 'location', 'inventory_item')
        }),
        ('Financial Information', {
            'fields': ('total_cost', 'payment_status', 'item_count')
        }),
        ('Authorization', {
            'fields': ('signed_by',)
        })
    )
    
    def changes_display(self, obj):
        history = list(obj.history.all())
        changes_list = []
        
        for i in range(1, min(11, len(history))):
            new_record = history[i-1]
            old_record = history[i]
            delta = new_record.diff_against(old_record)
            
            if delta.changes:
                change_time = new_record.history_date.strftime("%Y-%m-%d %H:%M:%S")
                change_user = new_record.history_user.username if new_record.history_user else "Unknown"
                changes = [f"{change.field}: '{change.old}' → '{change.new}'" for change in delta.changes]
                changes_list.append(f"<strong>{change_time} by {change_user}</strong><br>" + "<br>".join(changes))

        if changes_list:
            return mark_safe("<hr>".join(changes_list))
        return "No changes"

    changes_display.short_description = 'Last 10 Changes'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()  # Non-superusers see no records