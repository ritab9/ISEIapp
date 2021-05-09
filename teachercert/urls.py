from django.contrib import admin  #default admin site built by django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from users import views

urlpatterns = [
path('', views.loginpage, name='login'),
    ]