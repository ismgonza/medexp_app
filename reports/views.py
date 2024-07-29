from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from procedures.models import Procedure
from payments.models import Payment
from django.contrib.auth.models import User

class ReportsDashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'
    permission_required = 'reports.view_reports'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = self.request.GET.get('tab', 'procedures_by_location')
        context['start_date'] = self.request.GET.get('start_date', '')
        context['end_date'] = self.request.GET.get('end_date', '')
        return context

    def get_report_data(self, report_type):
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        procedures = Procedure.objects.all()
        if start_date and end_date:
            procedures = procedures.filter(procedure_date__range=[start_date, end_date])

        if report_type == 'procedures_by_location':
            return procedures.values('location__name', 'location__id')\
                .annotate(count=Count('id'), total_cost_sum=Sum('total_cost'))\
                .order_by('-count')
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

    def get(self, request, *args, **kwargs):
        if 'report_type' in request.GET:
            report_type = request.GET['report_type']
            data = self.get_report_data(report_type)
            return JsonResponse(list(data), safe=False)
        return super().get(request, *args, **kwargs)

    @method_decorator(require_POST)
    def get_detail_data(self, request):
        report_type = request.POST.get('report_type')
        item_id = request.POST.get('item_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        procedures = Procedure.objects.all()
        if start_date and end_date:
            procedures = procedures.filter(procedure_date__range=[start_date, end_date])

        if report_type == 'procedures_by_location':
            data = procedures.filter(location__id=item_id).values('procedure_date', 'patient__first_name', 'patient__last_name1', 'procedure_type', 'total_cost')
        elif report_type == 'procedures_by_signed_by':
            data = procedures.filter(signed_by__id=item_id).values('procedure_date', 'patient__first_name', 'patient__last_name1', 'procedure_type', 'total_cost')
        elif report_type == 'procedures_by_inventory_item':
            data = procedures.filter(inventory_item__id=item_id).values('procedure_date', 'patient__first_name', 'patient__last_name1', 'procedure_type', 'total_cost')
        elif report_type == 'procedures_by_status':
            data = procedures.filter(status=item_id).values('procedure_date', 'patient__first_name', 'patient__last_name1', 'procedure_type', 'total_cost')
        elif report_type == 'procedures_by_payment_status':
            data = procedures.filter(payment_status=item_id).values('procedure_date', 'patient__first_name', 'patient__last_name1', 'procedure_type', 'total_cost')
        elif report_type == 'payments_by_payment_method':
            payments = Payment.objects.filter(payment_method=item_id)
            if start_date and end_date:
                payments = payments.filter(payment_date__range=[start_date, end_date])
            data = payments.values('payment_date', 'patient__first_name', 'patient__last_name1', 'amount')
        else:
            data = []

        data_list = list(data)
        for item in data_list:
            if 'patient__first_name' in item and 'patient__last_name1' in item:
                item['patient_name'] = f"{item.pop('patient__first_name', '')} {item.pop('patient__last_name1', '')}".strip()
            # if 'payment_status' in item:
            #     item['payment_status'] = dict(Procedure.PAYMENT_STATUS_CHOICES).get(item['payment_status'], 'Unknown')

        return JsonResponse(data_list, safe=False)

class ReportDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'reports.view_reports'

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
        else:
            data = []

        return JsonResponse(list(data), safe=False)

    def post(self, request, *args, **kwargs):
        report_type = request.POST.get('report_type')
        item_id = request.POST.get('item_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

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

        data_list = list(data)

        for item in data_list:
            if 'patient__first_name' in item and 'patient__last_name1' in item:
                item['patient_name'] = f"{item.pop('patient__first_name', '')} {item.pop('patient__last_name1', '')}".strip()
            if 'status' in item:
                item['status'] = dict(Procedure.STATUS_CHOICES).get(item['status'], 'Unknown')
            if 'payment_status' in item:
                item['payment_status'] = dict(Procedure.PAYMENT_STATUS_CHOICES).get(item['payment_status'], 'Unknown')
            if report_type == 'payments_by_payment_method':
                item['payment_method'] = dict(Payment.PAYMENT_METHOD_CHOICES).get(item['payment_method'], 'Unknown')
                item['procedure_type'] = item.pop('procedure__procedure_type', 'N/A')
                item['procedure_id'] = item.pop('procedure__id', None)

        return JsonResponse(data_list, safe=False)