from django.urls import path
from . import views

urlpatterns = [
    path('isei_accreditation_dashboard/', views.isei_accreditation_dashboard, name='isei_accreditation_dashboard'),
    path('add_accreditation/', views.add_accreditation, name='add_accreditation'),
    path('edit_accreditation/<int:id>/', views.edit_accreditation, name='edit_accreditation'),
    path('delete_accreditation/<int:id>/', views.delete_accreditation, name='delete_accreditation'),
]