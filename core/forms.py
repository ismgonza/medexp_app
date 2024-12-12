from django import forms
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import Permission, Group
from .models import User
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

class UserForm(UserChangeForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False, label=_('Contraseña'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups', 'is_active')
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo'),
            'groups': _('Grupos'),
            'is_active': _('Activo'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['password'].help_text = _("Dejar vacío si no se cambia")
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = _("Ingrese una contraseña segura.")

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if self.instance.pk and not password:
            return None
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].label = _("Contraseña actual")
        self.fields["new_password1"].label = _("Nueva contraseña")
        self.fields["new_password2"].label = _("Confirmar nueva contraseña")
        
        # Override the help text
        self.fields['new_password1'].help_text = mark_safe(_(
            '<div class="password-help-text">'
            "Tu contraseña debe cumplir con los siguientes requisitos:<br>"
            "• No puede ser muy similar a tu otra información personal.<br>"
            "• Debe contener al menos 8 caracteres.<br>"
            "• No puede ser una contraseña de uso común.<br>"
            "• No puede ser completamente numérica."
            '</div>'
        ))
        
        self.error_messages['password_mismatch'] = _("Las dos contraseñas no coinciden.")
        self.error_messages['password_incorrect'] = _("Su contraseña antigua es incorrecta. Por favor, inténtelo de nuevo.")

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        
       # Custom password validation messages
        if len(password1) < 8:
            raise forms.ValidationError(_("Tu contraseña debe contener al menos 8 caracteres."))
        if password1.isdigit():
            raise forms.ValidationError(_("Tu contraseña no puede ser completamente numérica."))
        if password1.lower() in ['password', 'contraseña', '12345678', 'qwerty']:
            raise forms.ValidationError(_("Tu contraseña no puede ser una contraseña de uso común."))
        
        # You can add more custom validations here
        
        return password1
    
class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = _('Nueva contraseña')
        self.fields['new_password2'].label = _('Confirmar nueva contraseña')
        
        # Traducir los mensajes de ayuda
        self.fields['new_password1'].help_text = _(
            '<ul>'
            '<li>Su contraseña no puede ser similar a su información personal.</li>'
            '<li>Su contraseña debe contener al menos 8 caracteres.</li>'
            '<li>Su contraseña no puede ser una contraseña comúnmente utilizada.</li>'
            '<li>Su contraseña no puede ser completamente numérica.</li>'
            '</ul>'
        )