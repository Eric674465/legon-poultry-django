from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('verify-payment/<int:order_id>/', views.verify_payment, name='verify_payment'),
    path('download-report/', views.generate_pdf_report, name='generate_pdf_report'),
]