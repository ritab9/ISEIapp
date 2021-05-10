from django.contrib import admin  #default admin site built by django
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    #path('', views.loginpage, name='login'),
    # teacher urls

    path('myPDAdashboard/<str:pk>', views.myPDAdashboard, name='myPDAdashboard'),

    path('update_pdainstance/<str:pk>/', views.updatePDAinstance, name="update_pdainstance"),
    path('delete_pdainstance/<str:pk>/', views.deletePDAinstance, name="delete_pdainstance"),

    # create PDA instances and records. View submitted PDAs
    # new record: pk - user ID, sy- School-year,  #existing record: recId - record ID
    path('create_pda/<str:recId>/', views.createPDA, name='create_pda'),
    path('create_record/<str:pk>/<str:sy>/', views.createrecord, name='create_record'),

    # principal urls
#    path('principaldashboard/', views.principaldashboard, name='principal_dashboard'),
    # signs the record with recID
#    path('principaldashboard/<str:recID>', views.principaldashboard, name='principal_dashboard'),

    path('teachercertification/', views.teachercertification, name='teacher_certification'),
    # signs the record with recID
    path('teachercertification/<str:recID>', views.teachercertification, name='teacher_certification'),

    # admin urls
#    path('admindashboard/', views.admindashboard, name='admin_dashboard'),

]