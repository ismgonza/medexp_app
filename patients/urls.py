from django.urls import path
from .views import PatientListView, PatientCreateView, PatientUpdateView, PatientDeleteView, PatientDetailView, PatientSearchView, PadronSearchView, PatientBalanceListView



urlpatterns = [
    path('', PatientListView.as_view(), name='patient_list'),
    path('balances/', PatientBalanceListView.as_view(), name='patient_balance_list'),
    path('create/', PatientCreateView.as_view(), name='patient_create'),
    path('<int:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('<int:pk>/update/', PatientUpdateView.as_view(), name='patient_update'),
    path('<int:pk>/delete/', PatientDeleteView.as_view(), name='patient_delete'),
    path('search/', PatientSearchView.as_view(), name='patient_search'),
    path('search-padron/<str:id_number>/', PadronSearchView.as_view(), name='search_padron'),
]