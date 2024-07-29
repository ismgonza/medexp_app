from django import forms
from django.views.generic import CreateView, UpdateView
from django_filters.views import FilterView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.db import models, transaction
from .models import Payment
from .forms import PaymentForm
from procedures.models import Procedure
from patients.models import PatientBalance
from .filters import PaymentFilter
from django.shortcuts import get_object_or_404
from django.db.models import ExpressionWrapper, Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator
from decimal import Decimal
from django.contrib import messages
from patients.models import PatientBalance, CreditTransaction
from patients.views import PatientBalanceListView

class PaymentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'payments.add_payment'
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.procedure = get_object_or_404(Procedure, pk=self.kwargs['procedure_id'])
        kwargs['patient'] = self.procedure.patient
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['procedure'] = self.procedure
        patient_balance, created = PatientBalance.objects.get_or_create(patient=self.procedure.patient)
        context['amount_in_favor'] = patient_balance.amount_in_favor
        context['pending_amount'] = self.procedure.balance
        return context

    def form_valid(self, form):
        payment_amount = Decimal(form.cleaned_data['amount'])
        procedure_balance = self.procedure.balance
        payment_method = form.cleaned_data['payment_method']

        # Validate CREDIT payment amount
        if payment_method == 'CREDIT':
            if payment_amount > procedure_balance:
                form.add_error('amount', f"Si utiliza su balance (crédito), este no puede exceder ₡{procedure_balance} para este pago")
                return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save(commit=False)
            self.object.created_by = self.request.user
            self.object.procedure = self.procedure
            self.object.patient = self.procedure.patient

            patient_balance, created = PatientBalance.objects.get_or_create(patient=self.object.patient)

            if payment_method == 'CREDIT':
                if payment_amount > patient_balance.amount_in_favor:
                    form.add_error('amount', f"Insufficient credit. Available: ₡{patient_balance.amount_in_favor}")
                    return self.form_invalid(form)

                self.object.amount = payment_amount
                self.object.is_credit_payment = True
                patient_balance.amount_in_favor -= self.object.amount
            else:
                self.object.amount = payment_amount
                overpayment = max(payment_amount - procedure_balance, Decimal('0'))
                if overpayment > 0:
                    patient_balance.amount_in_favor += overpayment

            self.object.save()
            patient_balance.save()

            if self.object.is_credit_payment or overpayment > 0:
                CreditTransaction.objects.create(
                    patient_balance=patient_balance,
                    amount=self.object.amount if self.object.is_credit_payment else overpayment,
                    transaction_type='DECREASE' if self.object.is_credit_payment else 'INCREASE',
                    payment=self.object
                )

            self.procedure.update_payment_status()

            messages.success(self.request, f"Payment of ₡{self.object.amount} applied successfully. "
                                           f"New amount in favor: ₡{patient_balance.amount_in_favor}")

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('procedure_detail', kwargs={'pk': self.procedure.pk})

class PaymentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'payments.change_payment'
    model = Payment
    form_class = PaymentForm
    template_name = 'payments/payment_form.html'
    success_url = reverse_lazy('payment_list')

    def form_valid(self, form):
        # messages.success(self.request, 'Payment updated successfully.')
        return super().form_valid(form)

class PaymentListView(LoginRequiredMixin, PermissionRequiredMixin, FilterView):
    permission_required = 'payments.view_payment'
    model = Payment
    template_name = 'payments/payment_list.html'
    context_object_name = 'payments'
    filterset_class = PaymentFilter
    paginate_by = 10

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['payment_method_choices'] = Payment.PAYMENT_METHOD_CHOICES
        context['paginate_by'] = self.get_paginate_by(self.get_queryset())

        # Get patient balance data using PatientBalanceListView
        patient_balance_view = PatientBalanceListView()
        patient_balance_view.request = self.request
        patient_balance_queryset = patient_balance_view.get_queryset()

        # Paginate the balances
        balance_paginator = Paginator(patient_balance_queryset, self.get_paginate_by(patient_balance_queryset))
        balance_page = self.request.GET.get('balance_page', 1)
        context['balances'] = balance_paginator.get_page(balance_page)

        return context