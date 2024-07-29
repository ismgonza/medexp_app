from django import forms
from .models import Patient
from django.utils.translation import gettext_lazy as _

MEDICAL_CONDITIONS_LABELS = {
    'high_blood_pressure': _('Presión arterial alta'),
    'rheumatic_fever': _('Fiebre reumática'),
    'drug_addiction': _('Adicción a drogas'),
    'diabetes': _('Diabetes'),
    'anemia': _('Anemia'),
    'thyroid': _('Problemas de tiroides'),
    'asthma': _('Asma'),
    'arthritis': _('Artritis'),
    'cancer': _('Cáncer'),
    'heart_problems': _('Problemas cardíacos'),
    'smoker': _('Fumador'),
    'ulcers': _('Úlceras'),
    'gastritis': _('Gastritis'),
    'hepatitis': _('Hepatitis'),
    'kidney_diseases': _('Enfermedades renales'),
    'hormonal_problems': _('Problemas hormonales'),
    'epilepsy': _('Epilepsia'),
    'aids': _('SIDA'),
    'psychiatric_treatment': _('Tratamiento psiquiátrico')
}

class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['admission_date', 'created_by', 'updated_by']
        fields = '__all__'
        labels = {
            'id_number': _('Cédula'),
            'birth_date': _('Fecha de Nacimiento'),
            'first_name': _('Nombre(s)'),
            'last_name1': _('Primer Apellido'),
            'last_name2': _('Segundo Apellido'),
            'gender': _('Género'),
            'marital_status': _('Estado Civil'),
            'email': _('Correo Electrónico'),
            'primary_phone': _('Teléfono Principal'),
            'work_phone': _('Teléfono Trabajo'),
            'province': _('Provincia'),
            'canton': _('Cantón'),
            'district': _('Distrito'),
            'address_details': _('Detalle'),
            'emergency_contact1': _('Contacto 1'),
            'emergency_phone1': _('Teléfono'),
            'emergency_contact2': _('Contacto 2'),
            'emergency_phone2': _('Teléfono'),
            'admission_date': _('Fecha de Ingreso'),
            'referral_source': _('Cómo supo de nosotros?'),
            'consultation_reason': _('Motivo de la consulta'),
            'receive_notifications': _('Le gustaría recibir notificaciones sobre noticias y promociones?'),
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'province': forms.Select(attrs={'id': 'provincia'}),
            'canton': forms.Select(attrs={'id': 'canton'}),
            'district': forms.Select(attrs={'id': 'distrito'}),
            'address_details': forms.Textarea(attrs={'rows': 3}),
            'consultation_reason': forms.Textarea(attrs={'rows': 3}),
            'id_number': forms.TextInput(attrs={'placeholder': 'Sin guiones ni espacios, 112341234'}),
            'primary_phone': forms.TextInput(attrs={'placeholder': '+50612341234 o +11231231234'}),
            'work_phone': forms.TextInput(attrs={'placeholder': '+50612341234 o +11231231234'}),
            'emergency_phone1': forms.TextInput(attrs={'placeholder': '+50612341234 o +11231231234'}),
            'emergency_phone2': forms.TextInput(attrs={'placeholder': '+50612341234 o +11231231234'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['information_confirmed'].required = True
        self.fields['information_confirmed'].label = 'Hago constar que todas las respuestas son verdaderas y correctas. Si yo experimento algún cambio (anormal) en mi salud o en la toma de medicamentos, se lo informaré inmediatamente al odontólogo.'
        self.fields['under_treatment'].label = '¿Ha estado bajo algún tratamiento médico en los últimos años?'
        self.fields['current_medication'].label = '¿Toma alguna medicina actualmente?'
        self.fields['serious_illnesses'].label = '¿Ha sufrido enfermedades serias?'
        self.fields['surgeries'].label = '¿Ha sido operado?'
        self.fields['allergies'].label = '¿Es alérgico a algún medicamento o alimento?'
        self.fields['anesthesia_issues'].label = '¿Presenta condiciones anormales a la anestesia local (dental)?'
        self.fields['bleeding_issues'].label = '¿Sufre hemorragias después de un trauma?'
        self.fields['pregnant_or_lactating'].label = '(Mujeres) ¿Está embarazada o se encuentra en periodo de lactancia?'
        self.fields['contraceptives'].label = '(Mujeres) ¿Consume pastillas anticonceptivas?'
        self.fields['id_number'].help_text = "Ingrese la cédula sin espacios ni guiones"
        self.fields['primary_phone'].help_text = "Ingrese el número telefónico con el formato nacional o internacional correcto"
        self.fields['under_treatment_text'].label = ''
        self.fields['current_medication_text'].label = ''
        self.fields['serious_illnesses_text'].label = ''
        self.fields['surgeries_text'].label = ''
        self.fields['allergies_text'].label = ''

        # Medical conditions
        medical_conditions = [
            'high_blood_pressure', 'rheumatic_fever', 'drug_addiction', 'diabetes', 'anemia', 'thyroid',
            'asthma', 'arthritis', 'cancer', 'heart_problems', 'smoker', 'ulcers', 'gastritis', 'hepatitis',
            'kidney_diseases', 'hormonal_problems', 'epilepsy', 'aids', 'psychiatric_treatment'
        ]
        for condition in medical_conditions:
            self.fields[condition].label = MEDICAL_CONDITIONS_LABELS.get(condition, _(self.fields[condition].label))