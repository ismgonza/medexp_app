from django.urls import path
from .views import LocationListView, LocationCreateView, LocationUpdateView, LocationDeleteView, LocationDetailView

urlpatterns = [
    path('', LocationListView.as_view(), name='location_list'),
    path('create/', LocationCreateView.as_view(), name='location_create'),
    path('<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('<int:pk>/update/', LocationUpdateView.as_view(), name='location_update'),
    path('<int:pk>/delete/', LocationDeleteView.as_view(), name='location_delete'),
]