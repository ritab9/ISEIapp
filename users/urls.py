from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
# authentication urls + landing page url (landing is by default the login-page)
    path('', views.loginpage, name='login'),
    path('register/', views.registerpage, name='register'),
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
    path('staffdashboard/', views.staffdashboard, name='staff_dashboard'),
    path('teacherdashboard/', views.teacherdashboard, name='teacher_dashboard'),
    path('principaldashboard/', views.principaldashboard, name='principal_dashboard'),

    path('account_settings/<str:userID>/', views.accountsettings, name='account_settings'),

    #pk is teacher ID, appID is the last application ID
    path('teachercert_application/<str:pk>/<str:appID>/', views.teachercert_application, name='teachercert_application'),
    path('teachercert_application/<str:pk>/', views.teachercert_application, name='teachercert_application'),

]
