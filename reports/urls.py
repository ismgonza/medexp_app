from django.urls import path
from . import views

urlpatterns = [
    path('', views.ReportsDashboardView.as_view(), name='reports_dashboard'),
    path('detail/', views.ReportDetailView.as_view(), name='report_detail'),
]