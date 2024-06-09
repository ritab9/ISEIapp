from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
# authentication urls + landing page url (landing is by default the login-page)
    path('', views.logoutuser, name='logout'),
    path('register_teacher/', views.register_teacher, name='register_teacher'),
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logoutuser, name='logout'),

    path('admin/', views.loginpage, name='admin'),

    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
         name="reset_password"),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_sent.html"),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="users/password_reset_form.html"),
         name='password_reset_confirm'),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name="users/password_reset_complete.html"),
         name="password_reset_complete"),

    # dashboard urls
    path('principal_dashboard/<str:schoolID>/', views.principal_dashboard, name='principal_dashboard'),
    path('isei_dashboard/', views.isei_dashboard, name='isei_dashboard'),

    #teacher account settings
    path('account_settings/<str:userID>/', views.accountsettings, name='account_settings'),

    #path('transcript_status', views.transcript_status, name='transcript_status')
    path('update_school_info/<int:schoolID>/', views.update_school_info, name='update_school_info'),

]
