from django.urls import path
from . import views
from .views import ProcedureCreateView, ProcedureUpdateView, ProcedureDeleteView, ProcedureDetailView, ChangeProcedureStatusView, ProcedureListView

urlpatterns = [
    path('create/<int:patient_id>/', ProcedureCreateView.as_view(), name='procedure_create'),
    path('<int:pk>/', ProcedureDetailView.as_view(), name='procedure_detail'),
    path('<int:pk>/update/', ProcedureUpdateView.as_view(), name='procedure_update'),
    path('<int:pk>/delete/', ProcedureDeleteView.as_view(), name='procedure_delete'),
    path('<int:pk>/change-status/', ChangeProcedureStatusView.as_view(), name='change_procedure_status'),
    path('service-search/', views.ServiceSearchView.as_view(), name='service_search'),
    path('list/', ProcedureListView.as_view(), name='procedures_list'),
]