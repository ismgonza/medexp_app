from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from procedures.models import Procedure
from patients.models import Patient, PatientBalance
from .forms import ProcedureForm
from django.utils import timezone
from django.views import View
from django.http import JsonResponse
from inventory.models import InventoryItem
from django.db.models import Q
import json
from decimal import Decimal

class ProcedureCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'procedures.add_procedure'
    model = Procedure
    form_class = ProcedureForm
    template_name = 'procedures/procedure_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        patient_id = self.kwargs.get('patient_id')
        if patient_id:
            kwargs['initial'] = {'patient': patient_id}
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        self.patient = get_object_or_404(Patient, pk=self.kwargs['patient_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.patient.pk}) + '#procedureTabs'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient_id = self.kwargs.get('patient_id')
        context['inventory_items'] = InventoryItem.objects.filter(active=True)
        if patient_id:
            context['patient'] = get_object_or_404(Patient, pk=patient_id)
        return context

    def form_valid(self, form):
        # form.instance.procedure_date = timezone.now().date()
        # form.instance.signed_by = self.request.user
        form.instance.patient = self.patient
        if not form.instance.signed_by:
            form.instance.signed_by = self.request.user
        if not form.instance.procedure_date:
            form.instance.procedure_date = timezone.now().date()
            
        # Add debugging
        print(f"Form data: {form.cleaned_data}")
        print(f"Form is valid: {form.is_valid()}")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Add debugging for invalid form
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)
    

class ProcedureUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'procedures.change_procedure'
    model = Procedure
    form_class = ProcedureForm
    template_name = 'procedures/procedure_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inventory_items'] = InventoryItem.objects.filter(active=True)
        context['patient'] = self.object.patient
        return context
    
    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.object.patient.pk}) + '#procedureTabs'

    def form_valid(self, form):
        if not form.instance.signed_by:
            form.instance.signed_by = self.request.user
        # form.instance.updated_by = self.request.user
        
        # Add debugging
        print(f"Form data: {form.cleaned_data}")
        print(f"Form is valid: {form.is_valid()}")
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Add debugging for invalid form
        print(f"Form errors: {form.errors}")
        return super().form_invalid(form)
    
class ProcedureListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'procedures.view_procedure'
    model = Procedure
    template_name = 'procedures/procedure_list.html'
    context_object_name = 'procedures'

    def get_queryset(self):
        queryset = super().get_queryset()
        location = self.request.GET.get('location')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        if location:
            queryset = queryset.filter(location__name=location)
        if start_date and end_date:
            queryset = queryset.filter(procedure_date__range=[start_date, end_date])

        return queryset

class ProcedureDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'procedures.delete_procedure'
    model = Procedure
    template_name = 'procedures/procedure_confirm_delete.html'

    def get_success_url(self):
        return reverse('patient_detail', kwargs={'pk': self.object.patient.pk})

class ProcedureDetailView(DetailView):
    permission_required = 'procedures.view_procedure'
    model = Procedure
    template_name = 'procedures/procedure_detail.html'
    context_object_name = 'procedure'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['amount_in_favor'] = self.object.patient.balance.amount_in_favor if hasattr(self.object.patient, 'balance') else Decimal('0.00')
        return context
    
class ChangeProcedureStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'procedures.change_procedure'
    
    def post(self, request, pk):
        procedure = get_object_or_404(Procedure, pk=pk)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in dict(Procedure.STATUS_CHOICES):
            procedure.status = new_status
            procedure.save()
            return JsonResponse({
                'status': 'success',
                'statusText': procedure.get_status_display()
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status'
            }, status=400)
            
class ServiceSearchView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('query', '')
        services = InventoryItem.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query),
            active=True
        )[:10]  # Limit to 10 results
        data = [{'id': service.id, 'code': service.code, 'name': service.name, 'price': float(service.price)} for service in services]
        return JsonResponse(data, safe=False)