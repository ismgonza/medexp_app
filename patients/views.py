from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.urls import reverse_lazy, reverse
from .models import Patient
from .filters import PatientFilter, PatientSearchFilter
from payments.models import Payment
from payments.filters import PaymentFilter
from django_filters.views import FilterView
from .forms import PatientRegistrationForm
from django.http import JsonResponse, HttpResponse
import json, os
from django.core.cache import cache
from django.conf import settings
from django.core.paginator import Paginator
from django.template.loader import render_to_string

class PatientListView(PermissionRequiredMixin, LoginRequiredMixin, FilterView):
    permission_required = 'patients.view_patient'
    model = Patient
    template_name = 'patients/patient_list.html'
    filterset_class = PatientFilter
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_queryset(self):
        return Patient.objects.all().order_by('last_name1', 'last_name2', 'first_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())
        return context

class PatientDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'
    permission_required = 'patients.view_patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = self.request.user.has_perm('patients.change_patient')
        
        # Procedures
        pending_procedures = self.object.procedures.filter(status='PENDING').order_by('-procedure_date')
        processed_procedures = self.object.procedures.filter(status__in=['COMPLETED', 'CANCELED']).order_by('-procedure_date')
        
        pending_paginator = Paginator(pending_procedures, 10)
        pending_page_number = self.request.GET.get('pending_page', 1)
        context['pending_procedures'] = pending_paginator.get_page(pending_page_number)
        
        processed_paginator = Paginator(processed_procedures, 10)
        processed_page_number = self.request.GET.get('processed_page', 1)
        context['processed_procedures'] = processed_paginator.get_page(processed_page_number)
        
        # Payments
        payments = self.object.payments.all().order_by('-payment_date')
        payment_filter = PaymentFilter(self.request.GET, queryset=payments)
        filtered_payments = payment_filter.qs
        
        paginator = Paginator(filtered_payments, 10)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context['payments'] = page_obj
        context['filter'] = payment_filter
        context['paginate_by'] = 10
        context['payment_method_choices'] = Payment.PAYMENT_METHOD_CHOICES
        
        context['active_tab'] = self.request.GET.get('active_tab', 'details')

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if 'payment_method' in self.request.GET or 'payment_date' in self.request.GET or context['active_tab'] == 'payments':
                # This is a payment filter request
                html = render_to_string('payments/payment_list_content.html', context, request=self.request)
                return JsonResponse({'html': html})
            else:
                # This is a procedure request
                pending_html = render_to_string('procedures/procedure_table.html', {'procedures': context['pending_procedures'], 'procedure_type': 'pending'}, request=self.request)
                processed_html = render_to_string('procedures/procedure_table.html', {'procedures': context['processed_procedures'], 'procedure_type': 'processed'}, request=self.request)
                return JsonResponse({
                    'pending_html': pending_html,
                    'processed_html': processed_html
                })
        return super().render_to_response(context, **response_kwargs)

class PatientCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'patients.add_patient'
    model = Patient
    form_class = PatientRegistrationForm
    template_name = 'patients/patient_form.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.object.pk})

class PatientUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'patients.change_patient'
    model = Patient
    form_class = PatientRegistrationForm
    template_name = 'patients/patient_form.html'

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.object.pk})

class PatientDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    permission_required = 'patients.delete_patient'
    model = Patient
    template_name = 'patients/patient_confirm_delete.html'
    success_url = reverse_lazy('patient_list')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        # messages.success(self.request, 'Patient deleted successfully.')
        return response

class PatientSearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        patient_filter = PatientSearchFilter(data={'search': query}, queryset=Patient.objects.all())
        filtered_patients = patient_filter.qs
        
        data = [
            {
                'id': p.id, 
                'name': f"{p.first_name} {p.last_name1} {p.last_name2}", 
                'id_number': p.id_number
            } 
            for p in filtered_patients
        ]
        return JsonResponse(data, safe=False)
    
def load_padron_data():
    js_dir = os.path.join(settings.BASE_DIR, 'static', 'js')
    padron_files = [f for f in os.listdir(js_dir) if f.startswith('cr_padron_') and f.endswith('.json')]
    if not padron_files:
        return {}
    
    file_path = os.path.join(js_dir, padron_files[0])
    with open(file_path, 'r') as file:
        padron_data = json.load(file)
    
    return {person['id_number']: person for person in padron_data}

# # Load data when Django starts
# padron_index = load_padron_data()
# cache.set('padron_index', padron_index, None)  # Cache indefinitely

class PadronSearchView(View):
    def get(self, request, id_number):
        padron_index = cache.get('padron_index')
        if padron_index is None:
            padron_index = load_padron_data()
            cache.set('padron_index', padron_index, None)
        
        person = padron_index.get(id_number)
        if person:
            return JsonResponse({
                'found': True,
                'first_name': person['first_name'],
                'lastname1': person['lastname1'],
                'lastname2': person['lastname2']
            })
        else:
            return JsonResponse({'found': False})