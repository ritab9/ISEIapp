# annualvisits/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path("school_annual_visit/", views.school_annual_visit, name="school_annual_visit"),
    path("school_annual_visit/<int:school_id>", views.school_annual_visit, name="school_annual_visit"),

    path("isei_annual_visit/", views.isei_annual_visit, name="isei_annual_visit"),
    path("manage_annual_visits/", views.manage_annual_visits, name="manage_annual_visits"),

]
