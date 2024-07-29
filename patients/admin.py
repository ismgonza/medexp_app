from django.contrib import admin
from django.template.response import TemplateResponse
from .models import Patient, PatientBalance
from django.utils.safestring import mark_safe

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id_number', 'first_name', 'last_name1', 'last_name2', 'email', 'primary_phone', 'get_balance')
    search_fields = ('id_number', 'first_name', 'last_name1', 'last_name2', 'email')
    readonly_fields = ('admission_date', 'changes_display', 'get_balance')
    list_filter = ('gender', 'marital_status', 'admission_date')
    date_hierarchy = 'admission_date'

    fieldsets = (
        ('Personal Information', {
            'fields': ('id_number', 'first_name', 'last_name1', 'last_name2', 'birth_date', 'gender', 'marital_status')
        }),
        ('Contact Information', {
            'fields': ('email', 'primary_phone', 'work_phone')
        }),
        ('Address', {
            'fields': ('province', 'canton', 'district', 'address_details')
        }),
        ('Emergency Contacts', {
            'fields': ('emergency_contact1', 'emergency_phone1', 'emergency_contact2', 'emergency_phone2')
        }),
        ('Additional Data', {
            'fields': ('admission_date', 'referral_source', 'consultation_reason', 'receive_notifications')
        }),
        ('Medical History', {
            'fields': ('under_treatment', 'current_medication', 'serious_illnesses', 'surgeries', 'allergies', 
                       'anesthesia_issues', 'bleeding_issues', 'pregnant_or_lactating', 'contraceptives')
        }),
        ('Medical Conditions', {
            'fields': ('high_blood_pressure', 'rheumatic_fever', 'drug_addiction', 'diabetes', 'anemia', 'thyroid', 
                       'asthma', 'arthritis', 'cancer', 'heart_problems', 'smoker', 'ulcers', 'gastritis', 'hepatitis', 
                       'kidney_diseases', 'hormonal_problems', 'epilepsy', 'aids', 'psychiatric_treatment')
        }),
        ('Confirmation', {
            'fields': ('information_confirmed',)
        }),
        ('Balance', {
            'fields': ('get_balance',),
        })
    )
    
    def get_balance(self, obj):
        try:
            return obj.balance.amount_in_favor
        except PatientBalance.DoesNotExist:
            return "No balance"
    get_balance.short_description = 'Balance'
    
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

    # def last_modified(self, obj):
    #     return obj.history.latest().history_date
    # last_modified.short_description = 'Last Modified'

    def history_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        context = {
            'object_history': obj.history.all(),
            'object': obj,
        }
        context.update(extra_context or {})
        return TemplateResponse(request, "admin/patients/patient/history.html", context)
    
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
        return qs.none()   # Non-superusers see no records
    
@admin.register(PatientBalance)
class PatientBalanceAdmin(admin.ModelAdmin):
    list_display = ('patient', 'amount_in_favor', 'last_updated')
    search_fields = ('patient__first_name', 'patient__last_name1', 'patient__id_number')
    readonly_fields = ('last_updated',)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.none()   # Non-superusers see no records