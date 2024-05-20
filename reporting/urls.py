from django.urls import path
from . import views
from .views import StudentExcelDownload


urlpatterns = [
    path('student_report/<int:arID>/', views.student_report, name='student_report'),
    path('student_import_dashboard/<int:arID>/', views.student_import_dashboard, name='student_import_dashboard'),
    path('student_excel_download/', StudentExcelDownload.as_view(), name='student_excel_download'),
    path('student_report_display/<int:arID>/', views.student_report_display,
         name='student_report_display'),


    path('day190_report/<int:arID>/', views.day190_report, name='day190_report'),
    path('employee_report/<int:arID>/', views.employee_report, name='employee_report'),
    path('inservice_report/<int:arID>/', views.inservice_report, name='inservice_report'),
    path('opening_report/<int:arID>/', views.opening_report, name='opening_report'),
    path('ap_report/<int:arID>//', views.ap_report, name='ap_report'),

    path('day190_report_display/<int:arID>/', views.day190_report_display, name='day190_report_display'),
    path('employee_report_display/<int:arID>/', views.employee_report_display, name='employee_report_display'),
    path('inservice_report_display/<int:arID>/', views.inservice_report_display, name='inservice_report_display'),
    path('opening_report_display/<int:arID>/', views.opening_report_display, name='opening_report_display'),
    path('ap_report_display/<int:arID>//', views.ap_report_display, name='ap_report_display'),

]
