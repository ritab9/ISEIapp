from django.urls import path
from . import views

urlpatterns = [

    path('check-lock/<str:form_id>/', views.check_lock, name='check_lock'),
    path('acquire-lock/<str:form_id>/', views.acquire_lock, name='acquire_lock'),
    path('release-lock/<str:form_id>/', views.release_lock, name='release_lock'),

    path('setup_selfstudy/<int:accreditation_id>/', views.setup_selfstudy, name='setup_selfstudy'),
    path('selfstudy/<int:selfstudy_id>/', views.selfstudy, name='selfstudy'),

    path('<int:selfstudy_id>/selfstudy_profile/', views.selfstudy_profile, name='selfstudy_profile'),
    path('<int:selfstudy_id>/profile_history/', views.profile_history, name='profile_history'),
    path('<int:selfstudy_id>/profile_financial/', views.profile_financial, name='profile_financial'),
    path('<int:selfstudy_id>/profile_personnel/', views.profile_personnel, name='profile_personnel'),
    path('<int:selfstudy_id>/profile_student/', views.profile_student, name='profile_student'),
    path('<int:selfstudy_id>/profile_student_achievement/', views.profile_student_achievement, name='profile_student_achievement'),
    path('<int:selfstudy_id>/profile_secondary_curriculum/', views.profile_secondary_curriculum, name='profile_secondary_curriculum'),
    path('<int:selfstudy_id>/profile_support_services/', views.profile_support_services, name='profile_support_services'),
    path('<int:selfstudy_id>/profile_philanthropy/', views.profile_philanthropy, name='profile_philanthropy'),

    path('add_standardized_test_scores/<int:school_id>/<str:school_year_name>/<str:level_type>/', views.manage_standardized_test_scores, name='add_standardized_test_scores'),
    path('edit_standardized_test_scores/<int:session_id>/', views.manage_standardized_test_scores, name='edit_standardized_test_scores'),

    path('<int:selfstudy_id>/standard/<int:standard_id>/', views.selfstudy_standard, name='selfstudy_standard'),
    path('<int:selfstudy_id>/selfstudy_actionplan_instructions/', views.selfstudy_actionplan_instructions, name='selfstudy_actionplan_instructions'),
    path('<int:accreditation_id>/action_plan/', views.selfstudy_actionplan, name='selfstudy_actionplan_create'),
    path('<int:accreditation_id>/selfstudy_actionplan/<int:action_plan_id>/', views.selfstudy_actionplan,
         name='selfstudy_actionplan'),

    path('<int:selfstudy_id>/coordinating_team/', views.selfstudy_coordinating_team, name='selfstudy_coordinating_team'),
    path('add_coordinating_team_members/<int:selfstudy_id>/<int:team_id>/', views.add_coordinating_team_members, name='add_coordinating_team_members'),


    #path('<int:selfstudy_id>/completion/', views.selfstudy_completion, name='completion'),  # Optional completion page
]
