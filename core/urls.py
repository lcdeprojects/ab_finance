from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),

    # Pagamentos
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/new/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/', views.payment_detail, name='payment_detail'),
    path('payments/<int:pk>/edit/', views.payment_update, name='payment_update'),
    path('payments/<int:pk>/delete/', views.payment_delete, name='payment_delete'),
    
    # Controle e Financeiro
    path('payments/control/', views.payment_control, name='payment_control'),
    path('payments/defaults/', views.default_list, name='default_list'),
    path('payments/paid/', views.paid_list, name='paid_list'),
    path('installments/<int:pk>/update/', views.installment_update, name='installment_update'),
    path('installments/<int:pk>/delete/', views.paid_installment_delete, name='paid_installment_delete'),
    path('payments/export/', views.export_installments_excel, name='export_payments_excel'),
]
