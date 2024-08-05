from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Sum, F, Value, DecimalField, Case, When, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from procedures.models import Procedure
from payments.models import Payment
from django.db.models.functions import Coalesce, Concat
from patients.models import Patient
from django.contrib.auth.models import User


class ReportsDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'
    permission_required = 'reports.view_reports'

    def get(self, request, *args, **kwargs):
        if 'report_type' in request.GET:
            report_type = request.GET.get('report_type')
            if report_type:
                data = self.get_report_data(report_type)
                return JsonResponse(list(data) if data is not None else [], safe=False)
            else:
                return JsonResponse([], safe=False)
        return super().get(request, *args, **kwargs)

    def get_report_data(self, report_type):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        procedures = Procedure.objects.all()
        if start_date and end_date:
            procedures = procedures.filter(procedure_date__range=[start_date, end_date])

        if report_type == 'procedures_by_location':
            return procedures.values('location__name', 'location__id').annotate(count=Count('id'), total_cost_sum=Sum('total_cost')).order_by('-count')
        elif report_type == 'procedures_by_signed_by':
            return procedures.values('signed_by__username', 'signed_by__id').annotate(count=Count('id')).order_by('-count')
        elif report_type == 'procedures_by_inventory_item':
            return procedures.values('inventory_item__name', 'inventory_item__id').annotate(count=Count('id')).order_by('-count')
        elif report_type == 'procedures_by_status':
            return procedures.values('status').annotate(count=Count('id')).order_by('-count')
        elif report_type == 'procedures_by_payment_status':
            return procedures.values('payment_status').annotate(count=Count('id')).order_by('-count')
        elif report_type == 'payments_by_payment_method':
            payments = Payment.objects.all()
            if start_date and end_date:
                payments = payments.filter(payment_date__range=[start_date, end_date])
            return payments.values('payment_method').annotate(count=Count('id')).order_by('-count')
        elif report_type == 'patient_balances':
            if self.request.user.has_perm('patients.view_patient'):
                return Patient.objects.annotate(
                    patient_name=Concat('first_name', Value(' '), 'last_name1', Value(' '), 'last_name2'),
                    procedure_count=Count('procedures', filter=Q(procedures__payment_status__in=['PARTIAL', 'UNPAID'])),
                    total_procedures=Coalesce(Sum(Case(
                        When(procedures__payment_status__in=['PARTIAL', 'UNPAID'], then=F('procedures__total_cost')),
                        default=Value(0),
                        output_field=DecimalField()
                    )), Value(0, output_field=DecimalField())),
                    total_payments=Coalesce(Sum(Case(
                        When(procedures__payment_status__in=['PARTIAL', 'UNPAID'], then=F('procedures__payments__amount')),
                        default=Value(0),
                        output_field=DecimalField()
                    )), Value(0, output_field=DecimalField())),
                    calculated_balance=F('total_procedures') - F('total_payments'),
                    amount_in_favor=Coalesce('balance__amount_in_favor', Value(0, output_field=DecimalField()))
                ).values(
                    'id', 'patient_name', 'total_procedures', 'total_payments', 
                    'calculated_balance', 'amount_in_favor'
                ).order_by('last_name1', 'last_name2', 'first_name')
            else:
                return []
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        context['active_tab'] = self.request.GET.get('tab', 'procedures_by_location')
        context['can_view_patient_balance'] = self.request.user.has_perm('patients.view_patient')
        return context
    
    
class ReportDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'reports.view_reports'
    items_per_page = 10

    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('report_type')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        procedures = Procedure.objects.all()
        if start_date and end_date:
            procedures = procedures.filter(procedure_date__range=[start_date, end_date])

        if report_type == 'procedures_by_location':
            data = procedures.values('location__name', 'location__id').annotate(count=Count('id'))
        elif report_type == 'procedures_by_signed_by':
            data = procedures.values('signed_by__username', 'signed_by__id').annotate(count=Count('id'))
        elif report_type == 'procedures_by_inventory_item':
            data = procedures.values('inventory_item__name', 'inventory_item__id').annotate(count=Count('id'))
        elif report_type == 'procedures_by_status':
            data = procedures.values('status').annotate(count=Count('id'))
            data = [{'status': dict(Procedure.STATUS_CHOICES)[item['status']], 'count': item['count']} for item in data]
        elif report_type == 'procedures_by_payment_status':
            data = procedures.values('payment_status').annotate(count=Count('id'))
            data = [{'payment_status': dict(Procedure.PAYMENT_STATUS_CHOICES)[item['payment_status']], 'count': item['count']} for item in data]
        elif report_type == 'payments_by_payment_method':
            payments = Payment.objects.all()
            if start_date and end_date:
                payments = payments.filter(payment_date__range=[start_date, end_date])
            data = payments.values('payment_method').annotate(count=Count('id'))
            data = [{'payment_method': dict(Payment.PAYMENT_METHOD_CHOICES)[item['payment_method']], 'count': item['count']} for item in data]
        elif report_type == 'patient_balances':
            if self.request.user.has_perm('patients.view_patient'):
                data = Patient.objects.annotate(
                    procedure_count=Count('procedures', filter=Q(procedures__payment_status__in=['PARTIAL', 'UNPAID'])),
                    total_procedures=Coalesce(Sum(Case(
                        When(procedures__payment_status__in=['PARTIAL', 'UNPAID'], then=F('procedures__total_cost')),
                        default=Value(0),
                        output_field=DecimalField()
                    )), Value(0, output_field=DecimalField())),
                    total_payments=Coalesce(Sum(Case(
                        When(procedures__payment_status__in=['PARTIAL', 'UNPAID'], then=F('procedures__payments__amount')),
                        default=Value(0),
                        output_field=DecimalField()
                    )), Value(0, output_field=DecimalField())),
                    calculated_balance=F('total_procedures') - F('total_payments'),
                    amount_in_favor=Coalesce('balance__amount_in_favor', Value(0, output_field=DecimalField()))
                ).order_by('last_name1', 'last_name2', 'first_name').values(
                    'id', 'first_name', 'last_name1', 'last_name2', 'total_procedures',
                    'total_payments', 'calculated_balance', 'amount_in_favor'
                )
            else:
                data = []
        else:
            data = []

        return JsonResponse(list(data), safe=False)

    def post(self, request, *args, **kwargs):
        report_type = request.POST.get('report_type')
        item_id = request.POST.get('item_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        page = int(request.POST.get('page', 1))

        procedures = Procedure.objects.all()
        if start_date and end_date:
            procedures = procedures.filter(procedure_date__range=[start_date, end_date])
        
        if report_type == 'procedures_by_location':
            data = procedures.filter(location__id=item_id)
        elif report_type == 'procedures_by_signed_by':
            data = procedures.filter(signed_by__id=item_id)
        elif report_type == 'procedures_by_inventory_item':
            data = procedures.filter(inventory_item__id=item_id)
        elif report_type == 'procedures_by_status':
            data = procedures.filter(status=item_id)
        elif report_type == 'procedures_by_payment_status':
            data = procedures.filter(payment_status=item_id)
        elif report_type == 'payments_by_payment_method':
            payments = Payment.objects.filter(payment_method=item_id)
            if start_date and end_date:
                payments = payments.filter(payment_date__range=[start_date, end_date])
            data = payments.values(
                'id', 'payment_date', 'patient__id', 'patient__first_name', 'patient__last_name1',
                'amount', 'payment_method', 'procedure__id', 'procedure__procedure_type'
            )
        else:
            data = []

        if report_type != 'payments_by_payment_method':
            data = data.values(
                'id', 'procedure_date', 'patient__id', 'patient__first_name', 'patient__last_name1',
                'procedure_type', 'total_cost', 'status', 'payment_status'
            )

        paginator = Paginator(list(data), self.items_per_page)
        page_obj = paginator.get_page(page)

        data_list = list(page_obj)

        for item in data_list:
            if 'patient__first_name' in item and 'patient__last_name1' in item:
                item['patient_name'] = f"{item.pop('patient__first_name', '')} {item.pop('patient__last_name1', '')}".strip()
            if 'status' in item:
                item['status'] = dict(Procedure.STATUS_CHOICES).get(item['status'], 'Unknown')
            if 'payment_status' in item:
                item['payment_status'] = dict(Procedure.PAYMENT_STATUS_CHOICES).get(item['payment_status'], 'Unknown')
            if report_type == 'payments_by_payment_method':
                item['payment_method'] = dict(Payment.PAYMENT_METHOD_CHOICES).get(item.get('payment_method'), 'Unknown')
                item['procedure_type'] = item.pop('procedure__procedure_type', 'N/A')
                item['procedure_id'] = item.pop('procedure__id', None)

        return JsonResponse({
            'results': data_list,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }
        })
