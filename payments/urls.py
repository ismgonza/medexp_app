from django.urls import path
from .views import PaymentCreateView, PaymentListView, PaymentUpdateView

urlpatterns = [
    path('create/<int:procedure_id>/', PaymentCreateView.as_view(), name='payment_create'),
    path('<int:pk>/update/', PaymentUpdateView.as_view(), name='payment_update'),
    path('list/', PaymentListView.as_view(), name='payment_list'),
]