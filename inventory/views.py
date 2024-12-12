from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from .models import InventoryItem
from .forms import InventoryItemForm
from .filters import filter_inventory_items

class InventoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = InventoryItem
    template_name = 'inventory/inventoryitem_list.html'
    context_object_name = 'items'
    permission_required = 'inventory.view_inventoryitem'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search')
        show_inactive = self.request.GET.get('show_inactive') == 'on'
        
        return filter_inventory_items(queryset, search_query, show_inactive)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['show_inactive'] = self.request.GET.get('show_inactive') == 'on'
        return context

class InventoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/inventoryitem_form.html'
    success_url = reverse_lazy('inventory_list')
    permission_required = 'inventory.add_inventoryitem'

    def form_valid(self, form):
        messages.success(self.request, 'Inventory item created successfully.')
        return super().form_valid(form)

class InventoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = InventoryItem
    form_class = InventoryItemForm
    template_name = 'inventory/inventoryitem_form.html'
    success_url = reverse_lazy('inventory_list')
    permission_required = 'inventory.change_inventoryitem'

    def form_valid(self, form):
        messages.success(self.request, 'Inventory item updated successfully.')
        return super().form_valid(form)

class InventoryDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = InventoryItem
    template_name = 'inventory/inventoryitem_confirm_delete.html'
    success_url = reverse_lazy('inventory_list')
    permission_required = 'inventory.delete_inventoryitem'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Inventory item deleted successfully.')
        return super().delete(request, *args, **kwargs)