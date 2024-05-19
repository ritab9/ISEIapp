from django.urls import path
from . import views
from .views import StudentExcelDownload


urlpatterns = [
    path('student_report/<int:arID>/', views.student_report, name='student_report'),
    path('student_import_dashboard/<int:arID>/', views.student_import_dashboard, name='student_import_dashboard'),
    path('student_excel_download/', StudentExcelDownload.as_view(), name='student_excel_download'),

    path('day190_report/<int:arID>/', views.day190_report, name='day190_report'),
    path('employee_report/<int:arID>/', views.employee_report, name='employee_report'),
    path('inservice_report/<int:arID>/', views.inservice_report, name='inservice_report'),
    path('opening_report/<int:arID>/', views.opening_report, name='opening_report'),
    path('ap_report/<int:arID>//', views.ap_report, name='ap_report'),

]
