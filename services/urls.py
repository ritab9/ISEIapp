from django.urls import path
from . import views

urlpatterns = [
    path('test_order/<int:schoolID>/', views.test_order, name='test_order'),
    path('test_order/<int:schoolID>/<int:orderID>/', views.test_order, name='test_order'),
]