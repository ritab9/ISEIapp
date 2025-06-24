from django.urls import path
from . import views
from .views import StudentExcelDownload, PersonnelListView


urlpatterns = [
    #individual school reporting
    path('student_report/<int:arID>/', views.student_report, name='student_report'),
    path('student_import_dashboard/<int:arID>/', views.student_import_dashboard, name='student_import_dashboard'),
    path('student_excel_download/', StudentExcelDownload.as_view(), name='student_excel_download'),
    path('student_report_display/<int:arID>/', views.student_report_display,
         name='student_report_display'),
    path('import_students_prev_year/<int:arID>/', views.import_students_prev_year, name='import_students_prev_year'),
    path('tn_student_export/<int:arID>/', views.tn_student_export, name='tn_student_export'),

    path('employee_report/<int:arID>/', views.employee_report, name='employee_report'),
    path('employee/report/<int:arID>/all/', views.employee_report, {'show_all': True}, name='employee_report_all'),
    path('employee_add_edit/<int:arID>/<int:personnelID>/', views.employee_add_edit, name='employee_edit'),
    path('employee_add_edit/<int:arID>/<str:positionCode>/', views.employee_add_edit, name='employee_add'),
    path('import_employee_prev_year/<int:arID>/', views.import_employee_prev_year, name='import_employee_prev_year'),

    path('day190_report/<int:arID>/', views.day190_report, name='day190_report'),
    path('inservice_report/<int:arID>/', views.inservice_report, name='inservice_report'),
    path('opening_report/<int:arID>/', views.opening_report, name='opening_report'),
    path('closing_report/<int:arID>/', views.closing_report, name='closing_report'),

    path('ap_report/<int:arID>//', views.ap_report, name='ap_report'),

    path('day190_report_display/<int:arID>/', views.day190_report_display, name='day190_report_display'),
    path('employee_report_display/<int:arID>/', views.employee_report, name='employee_report_display'),
    path('inservice_report_display/<int:arID>/', views.inservice_report_display, name='inservice_report_display'),
    path('opening_report_display/<int:arID>/', views.opening_report_display, name='opening_report_display'),
    path('closing_report_display/<int:arID>/', views.closing_report_display, name='closing_report_display'),

    path('worthy_student_scholarship/<int:arID>/', views.worthy_student_scholarship, name='worthy_student_scholarship'),
    path('worthy_student_scholarship_display/<int:arID>/', views.worthy_student_scholarship_display, name='worthy_student_scholarship_display'),

    path('ap_report_display/<int:arID>//', views.ap_report_display, name='ap_report_display'),


    #directories
    path('school_directory/', views.school_directory, name='school_directory'),
    path('personnel_directory/', PersonnelListView.as_view(), name='personnel_directory'),
    path('personnel_directory/<str:schoolID>/', PersonnelListView.as_view(), name='personnel_directory'),
    path('school_personnel_directory/', views.school_personnel_directory, name='school_personnel_directory'),

    #isei
    path('isei_reporting_dashboard/', views.isei_reporting_dashboard, name='isei_reporting_dashboard'),
    path('isei_worthy_student_scholarship/', views.isei_worthy_student_scholarship, name='isei_worthy_student_scholarship'),


    #Data Analysis

    #Staff Retention
    path('staff_retention_school/<int:schoolID>/', views.staff_retention_school, name='staff_retention_school'),
    path('staff_retention_all/', views.staff_retention_all, name='staff_retention_all'),

    #Student Enrollment
    path('longitudinal_enrollment/', views.longitudinal_enrollment, name='longitudinal_enrollment'),
    path('longitudinal_enrollment/<str:individual_school_name>/', views.longitudinal_enrollment, name='longitudinal_enrollment_single'),

    path('add_enrollment/<str:school_name>/<str:year_name>/', views.add_enrollment, name='add_enrollment_with_school_year'),
    path('add_enrollment/<str:school_name>/', views.add_enrollment, name='add_enrollment_with_school'),
    path('add_enrollment/', views.add_enrollment, name='add_enrollment'),


    #ajax
    path('ajax/get-teacher-email/', views.get_teacher_email, name="get_teacher_email"),

    #Reporting
    path('TN_reports/download/<str:schoolyearID>', views.download_TN_reports, name='download_TN_reports'),
    path('NCPSA_directory/download/<str:schoolyearID>', views.download_NCPSA_directory, name='download_NCPSA_directory'),

]
