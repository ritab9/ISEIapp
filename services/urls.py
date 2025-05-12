#service/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('test_order_dashboard/<int:schoolID>/', views.test_order_dashboard, name='test_order_dashboard'),

    path('test_order/<int:schoolID>/', views.test_order, name='test_order'),
    path('test_order/<int:schoolID>/<int:orderID>/', views.test_order, name='test_order'),

    path('isei_test_order/', views.isei_test_order, name='isei_test_order'),
    path('finalize_order/<int:order_id>/', views.finalize_order, name='finalize_order'),

    path('resources/', views.resources, name='resources'),

    path('calendar/', views.calendar, name='calendar'),
]