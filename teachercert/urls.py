from django.contrib import admin  #default admin site built by django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [

    path('teacherdashboard/<str:userID>/', views.teacherdashboard, name='teacher_dashboard'),
    path('principalteachercert/<str:schoolID>/', views.principalteachercert, name='principal_teachercert'),
    path('isei_teachercert_dashboard/', views.isei_teachercert_dashboard, name='isei_teachercert_dashboard'),
    #path('iseiteachers/', views.isei_teachers, name='isei_teachers'),

    # teacher urls pk - teacher.id
    path('myCEUdashboard/<str:pk>/', views.myCEUdashboard, name='myCEUdashboard'),
    path('my_academic_classes/<str:pk>/', views.my_academic_classes, name='my_academic_classes'),

    path('update_ceuinstance/<str:pk>/', views.updateCEUinstance, name="update_ceuinstance"),
    path('delete_ceuinstance/<str:pk>/', views.deleteCEUinstance, name="delete_ceuinstance"),
    path('update_academic_class/<str:pk>/', views.update_academic_class, name="update_academic_class"),
    path('delete_academic_class/<str:pk>/', views.delete_academic_class, name="delete_academic_class"),

    path('ceu_info/', views.ceu_info, name="ceu_info"),

    # create PDA instances and reports. View submitted PDAs
    # new record: pk - user ID, sy- School-year,  #existing record: recId - record ID
    path('create_ceu/<str:recId>/', views.createCEU, name='create_ceu'),
    path('create_report/<str:pk>/<str:sy>/', views.createCEUreport, name='create_report'),
# Ajax for dependent dropdowns and info
    path('ajax/load_CEUtypes/', views.load_CEUtypes, name = 'ajax_load_CEUtypes'),
    path('ajax/load_evidence/', views.load_evidence, name = 'ajax_load_evidence'),

#if we want the add the ceuInstance separately (actually, if we do that we should just reuse update!)
#    path('add_instance/<str:reportID>/',views.add_instance, name='add_instance'),

    #pk is teacher ID
    path('teachercert_application/<str:pk>/', views.teachercert_application, name='teachercert_application'),
    path('teachercert_application_done/<str:pk>/', views.teachercert_application_done, name='teachercert_application_done'),


    # principal urls
    #path('principal_teachercert/', views.principal_teachercert, name='principal_teachercert'),
    path('principal_ceu_approval/', views.principal_ceu_approval, name='principal_ceu_approval'),
    path('principal_ceu_approval/<str:recID>/', views.principal_ceu_approval, name='principal_ceu_approval'),
    path('principal_ceu_approval/<str:recID>/<str:instID>/', views.principal_ceu_approval, name='principal_ceu_approval'),
    path('background_check/<str:schoolid>/', views.mark_background_check, name='background_check'),

    # isei staff and principal urls
    path('CEUreports/', views.CEUreports, name='CEUreports'),

    # isei staff urls
    path('isei_teachercert/', views.isei_teachercert, name='isei_teachercert'),

    path('manage_tcertificate/<str:pk>/', views.manage_tcertificate, name='manage_tcertificate'),
    path('manage_tcertificate/<str:pk>/<str:certID>/', views.manage_tcertificate, name='manage_tcertificate'),
    path('delete_tcertificate/<str:certID>/', views.delete_tcertificate, name='delete_tcertificate'),
#attempt to create and print the certificate directly
    path('create_certificate/<str:certID>/', views.create_certificate, name='create_certificate'),

    path('ajax/load_renewal/', views.load_renewal, name='ajax_load_renewal'),

    path('archive_tcertificate/<str:cID>/<str:certID>/', views.archive_tcertificate, name='archive_tcertificate'),
    path('de_archive_tcertificate/<str:cID>/<str:certID>/', views.de_archive_tcertificate, name='de_archive_tcertificate'),

    path('isei_ceu_approval/', views.isei_ceu_approval, name='isei_ceu_approval'),

    path('isei_ceu_approval/', views.isei_ceu_approval, name='isei_ceu_approval'),
    path('isei_ceu_approval/<str:repID>/', views.isei_ceu_approval, name='isei_ceu_approval'),
    path('isei_ceu_approval/<str:repID>/<str:instID>/', views.isei_ceu_approval, name='isei_ceu_approval'),
    path('isei_ceu_report_approval/<str:repID>', views.isei_ceu_report_approval,name='isei_ceu_report_approval'),
    path('isei_ceu_report_approval/<str:repID>/<str:instID>/', views.isei_ceu_report_approval, name='isei_ceu_report_approval'),

    #pdf of approved activities - unused
    #path('approved_pdf/', views.approved_pdf, name='approved_pdf'),
    #path('approved_pdf2/', views.approved_pdf2, name='approved_pdf2'),

    path('bulk_ceu_entry/', views.bulk_ceu_entry, name='bulk_ceu_entry'),

    path('add_ISEI_CEUs/', views.add_ISEI_CEUs, name='add_ISEI_CEUs'),
    path('isei_teacher_applications/', views.isei_teacher_applications, name='isei_teacher_applications'),
    path('isei_manage_application/<str:appID>/',views.isei_manage_application, name = 'isei_manage_application'),

    path('standard_checklist/<str:teacherID>/', views.standard_checklist, name = 'standard_checklist'),

    path("school/<int:school_id>/checklist-summary/", views.school_checklist_summary, name="school_checklist_summary"),
    path("isei/checklist-summary/", views.isei_checklist_summary, name="isei_checklist_summary"),
]