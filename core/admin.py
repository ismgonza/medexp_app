from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from .models import User, UserPreference

class CustomGroupAdmin(BaseGroupAdmin):
    list_display = ('name',)

    def get_permissions(self, obj):
        return format_html('<br>'.join([f"{p.content_type.app_label} | {p.content_type.model} | {p.name}" for p in obj.permissions.all()]))
    get_permissions.short_description = 'Permissions'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        group = self.get_object(request, object_id)
        if group:
            extra_context['selected_permissions'] = group.permissions.all()
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'get_user_groups', 'get_user_permissions', 'is_staff', 'is_active')
    list_filter = ('groups', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'groups', 'is_active', 'user_permissions')}
        ),
    )
    
    def get_user_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_user_groups.short_description = 'User Groups'
    
    def get_user_permissions(self, obj):
        return ", ".join([f"{perm.content_type.app_label}.{perm.codename}" for perm in obj.user_permissions.all()])
    get_user_permissions.short_description = 'User Permissions'

class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'value')
    list_filter = ('user',)
    search_fields = ('user__username', 'key', 'value')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)
admin.site.register(UserPreference, UserPreferenceAdmin)