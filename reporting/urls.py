from django.urls import path
from . import views


urlpatterns = [

    path('day190_report/<int:schoolID>/<int:school_yearID>/', views.day190_report, name='day190_report'),
    path('student_report/<int:schoolID>/<int:school_yearID>/', views.student_report, name='student_report'),
    path('employee_report/<int:schoolID>/<int:school_yearID>/', views.employee_report, name='employee_report'),
    path('inservice_report/<int:schoolID>/<int:school_yearID>/', views.inservice_report, name='inservice_report'),
    path('opening_report/<int:schoolID>/<int:school_yearID>/', views.opening_report, name='opening_report'),
    path('ap_report/<int:schoolID>/<int:school_yearID>/', views.ap_report, name='ap_report'),

]
