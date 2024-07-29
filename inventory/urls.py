from django.urls import path
from . import views

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='inventory_list'),
    path('create/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('update/<int:pk>/', views.InventoryUpdateView.as_view(), name='inventory_update'),
    path('delete/<int:pk>/', views.InventoryDeleteView.as_view(), name='inventory_delete'),
]