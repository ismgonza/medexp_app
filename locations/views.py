# locations/views.py
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from .models import Location
from .forms import LocationForm

class LocationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    permission_required = 'locations.view_location'
    model = Location
    template_name = 'locations/location_list.html'

class LocationDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    permission_required = 'locations.view_location'
    model = Location
    template_name = 'locations/location_detail.html'
    context_object_name = 'location'

class LocationCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'locations.add_location'
    model = Location
    form_class = LocationForm
    template_name = 'locations/location_form.html'
    success_url = reverse_lazy('location_list')

class LocationUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'locations.change_location'
    model = Location
    form_class = LocationForm
    template_name = 'locations/location_form.html'
    success_url = reverse_lazy('location_list')

class LocationDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'locations.delete_location'
    model = Location
    template_name = 'locations/location_confirm_delete.html'
    success_url = reverse_lazy('location_list')