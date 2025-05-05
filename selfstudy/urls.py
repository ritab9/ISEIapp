from django.urls import path
from . import views

urlpatterns = [

    path('check-lock/<str:form_id>/', views.check_lock, name='check_lock'),
    path('acquire-lock/<str:form_id>/', views.acquire_lock, name='acquire_lock'),
    path('release-lock/<str:form_id>/', views.release_lock, name='release_lock'),

    path('setup_selfstudy/<int:accreditation_id>/', views.setup_selfstudy, name='setup_selfstudy'),
    path('selfstudy/<int:selfstudy_id>/', views.selfstudy, name='selfstudy'),

    path('<int:selfstudy_id>/selfstudy_profile/', views.selfstudy_profile, name='selfstudy_profile'),
    path('<int:selfstudy_id>/selfstudy_profile/read_only/', views.selfstudy_profile, {'readonly': True}, name='selfstudy_profile_readonly'),

    path('<int:selfstudy_id>/profile_history/', views.profile_history, name='profile_history'),
    path('<int:selfstudy_id>/profile_history/read_only/', views.profile_history, {'readonly': True}, name='profile_history_readonly'),

    path('<int:selfstudy_id>/profile_financial/', views.profile_financial, name='profile_financial'),
    path('<int:selfstudy_id>/profile_financial/read_only/', views.profile_financial, {'readonly': True}, name='profile_financial_readonly'),

    path('<int:selfstudy_id>/profile_personnel/', views.profile_personnel, name='profile_personnel'),
    path('<int:selfstudy_id>/profile_personnel/read_only/', views.profile_personnel, {'readonly': True}, name='profile_personnel_readonly'),

    path('<int:selfstudy_id>/profile_student/', views.profile_student, name='profile_student'),
    path('<int:selfstudy_id>/profile_student/read_only/', views.profile_student, {'readonly': True}, name='profile_student_readonly'),

    path('<int:selfstudy_id>/profile_student_achievement/', views.profile_student_achievement, name='profile_student_achievement'),
    path('<int:selfstudy_id>/profile_student_achievement/read_only/', views.profile_student_achievement, {'readonly': True},
         name='profile_student_achievement_readonly'),

    path('add_standardized_test_scores/<int:school_id>/<str:school_year_name>/<str:level_type>/', views.manage_standardized_test_scores, name='add_standardized_test_scores'),
    path('edit_standardized_test_scores/<int:session_id>/', views.manage_standardized_test_scores, name='edit_standardized_test_scores'),


    path('<int:selfstudy_id>/profile_secondary_curriculum/', views.profile_secondary_curriculum, name='profile_secondary_curriculum'),
    path('<int:selfstudy_id>/profile_secondary_curriculum/read_only/', views.profile_secondary_curriculum, {'readonly': True},
         name='profile_secondary_curriculum_readonly'),

    path('<int:selfstudy_id>/profile_support_services/', views.profile_support_services, name='profile_support_services'),
    path('<int:selfstudy_id>/profile_support_services/read_only/', views.profile_support_services, {'readonly': True},
         name='profile_support_services_readonly'),

    path('<int:selfstudy_id>/profile_philanthropy/', views.profile_philanthropy, name='profile_philanthropy'),
    path('<int:selfstudy_id>/profile_philanthropy/read_only/', views.profile_philanthropy, {'readonly': True}, name='profile_philanthropy_readonly'),


    path('<int:selfstudy_id>/standard/<int:standard_id>/', views.selfstudy_standard, name='selfstudy_standard'),
    path('<int:selfstudy_id>/standard/<int:standard_id>/read_only/', views.selfstudy_standard, {'readonly': True}, name='selfstudy_standard_readonly'),

    path('<int:selfstudy_id>/selfstudy_actionplan_instructions/', views.selfstudy_actionplan_instructions, name='selfstudy_actionplan_instructions'),

    path('<int:accreditation_id>/action_plan/', views.selfstudy_actionplan, name='selfstudy_actionplan_create'),

    path('<int:accreditation_id>/selfstudy_actionplan/<int:action_plan_id>/', views.selfstudy_actionplan,
         name='selfstudy_actionplan'),
    path('<int:accreditation_id>/selfstudy_actionplan/<int:action_plan_id>/read_only/', views.selfstudy_actionplan, {'readonly': True},
         name='selfstudy_actionplan_readonly'),

    path('<int:selfstudy_id>/coordinating_team/', views.selfstudy_coordinating_team, name='selfstudy_coordinating_team'),
    path('<int:selfstudy_id>/coordinating_team/read_only/', views.selfstudy_coordinating_team, {'readonly': True}, name='selfstudy_coordinating_team_readonly'),

    path('add_coordinating_team_members/<int:selfstudy_id>/<int:team_id>/', views.add_coordinating_team_members, name='add_coordinating_team_members'),


    #path('<int:selfstudy_id>/completion/', views.selfstudy_completion, name='completion'),  # Optional completion page
]
