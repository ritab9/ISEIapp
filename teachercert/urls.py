from django.contrib import admin  #default admin site built by django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [

    # teacher urls
    path('myPDAdashboard/<str:pk>', views.myPDAdashboard, name='myPDAdashboard'),
    path('update_pdainstance/<str:pk>/', views.updatePDAinstance, name="update_pdainstance"),
    path('delete_pdainstance/<str:pk>/', views.deletePDAinstance, name="delete_pdainstance"),
    path('update_academic_class/<str:pk>/', views.update_academic_class, name="update_academic_class"),
    path('delete_academic_class/<str:pk>/', views.delete_academic_class, name="delete_academic_class"),

    path('ceu_info/', views.ceu_info, name="ceu_info"),

    # create PDA instances and reports. View submitted PDAs
    # new record: pk - user ID, sy- School-year,  #existing record: recId - record ID
    path('create_pda/<str:recId>/', views.createPDA, name='create_pda'),
    path('create_report/<str:pk>/<str:sy>/', views.createPDAreport, name='create_report'),

    # principal urls
    path('principal_teachercert/', views.principal_teachercert, name='principal_teachercert'),
    path('principal_pda_approval/', views.principal_pda_approval, name='principal_pda_approval'),
    path('principal_pda_approval/<str:recID>', views.principal_pda_approval, name='principal_pda_approval'),
    path('principal_pda_approval/<str:recID>/<str:instID>', views.principal_pda_approval, name='principal_pda_approval'),

    # isei staff urls
    path('isei_teachercert/', views.isei_teachercert, name='isei_teachercert'),
    path('isei_PDAreports/', views.isei_PDAreports, name='isei_PDAreports'),

    path('isei_pda_approval/', views.isei_pda_approval, name='isei_pda_approval'),
    path('isei_pda_approval/<str:repID>', views.isei_pda_approval, name='isei_pda_approval'),
    path('isei_pda_approval/<str:repID>/<str:instID>', views.isei_pda_approval, name='isei_pda_approval'),

    #pdf of approved activities
    path('approved_pdf/', views.approved_pdf, name='approved_pdf')
]