
from django.urls import path

from . import views

urlpatterns = [

    path('contact_isei/<str:userID>', views.ContactISEI, name='contactisei'),
    path('sendemailsattachments/', views.SendEmailsAttachments, name='sendemailsattachments'),
    path('email_registered_user_view/<int:teacherID>/', views.email_registered_user_view, name='email_registered_user_view'),

    path('send_email_selfstudy_coordinating_team/<int:selfstudy_id>/', views.send_email_selfstudy_coordinating_team, name='send_email_selfstudy_coordinating_team'),
]