from django.urls import path
from . import views


urlpatterns = [

    #ISEI APR addition links
    path('manage_apr/<int:accreditation_id>/', views.manage_apr, name='manage_apr'),
    path('apr/<int:apr_id>/add_action_plan_directives/', views.add_action_plan_directives, name='add_action_plan_directives'),
    path('apr/<int:apr_id>/add_priority_directives/', views.add_priority_directives, name='add_priority_directives'),
    path('apr/<int:apr_id>/add_directives/', views.add_directives, name='add_directives'),
    path('apr/<int:apr_id>/add_recommendations/', views.add_recommendations, name='add_recommendations'),

    path('apr/<int:accreditation_id>/action_plan/', views.manage_action_plan, name='add_action_plan'),
    path('apr/<int:accreditation_id>/action_plan/<int:action_plan_id>/', views.manage_action_plan, name='edit_action_plan'),

    path('apr_progress_report/<int:apr_id>/', views.apr_progress_report, name='apr_progress_report'),
    path('update_progress/<int:progress_id>/', views.update_progress, name='update_progress'),
    path('update_progress_status/', views.update_progress_status, name='update_progress_status'),
    path('update_actionplandirective_completed_date/', views.update_actionplandirective_completed_date, name='update_actionplandirective_completed_date'),

]