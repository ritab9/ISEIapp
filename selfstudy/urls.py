from django.urls import path
from . import views

urlpatterns = [
    path('setup_selfstudy/<int:accreditation_id>/', views.setup_selfstudy, name='setup_selfstudy'),
    path('selfstudy/<int:selfstudy_id>/', views.selfstudy, name='selfstudy'),

    path('<int:selfstudy_id>/profile/', views.selfstudy_profile, name='profile'),
    path('<int:selfstudy_id>/standard/<int:standard_id>/', views.selfstudy_standard, name='standard'),

    #path('<int:selfstudy_id>/completion/', views.selfstudy_completion, name='completion'),  # Optional completion page
]
