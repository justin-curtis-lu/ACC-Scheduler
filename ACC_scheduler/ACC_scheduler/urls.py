"""ACC_scheduler URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from scheduling_application import views as sa_views

urlpatterns = [
    path('', sa_views.home, name='home'),
    path('console/', sa_views.console, name='console'),
    path('admin/', admin.site.urls),
    path('register/', sa_views.register, name='register'),
    path('keys/', sa_views.keys, name='keys'),
    path('login/', sa_views.login, name='login'),
    path('logout/', sa_views.logout, name='logout'),
    path('success/', sa_views.success, name='confirmation_received'),
    path('make_appointment/', sa_views.make_appointment, name='make_appointment'),
    path('confirm_v', sa_views.confirm_volunteers, name='confirm_volunteers'),
    path('view_seniors/', sa_views.view_seniors, name='view_seniors'),
    path('add_senior/', sa_views.add_senior, name='add_senior'),
    path('senior/<str:pk>', sa_views.senior_page, name='senior_page'),
    path('edit_senior/<str:pk>', sa_views.edit_senior, name='edit_senior'),
    path('view_volunteers/', sa_views.view_volunteers, name='view_volunteers'),
    path('add_volunteer/', sa_views.add_volunteer, name='add_volunteer'),
    path('galaxy_update_volunteers/', sa_views.galaxy_update_volunteers, name='galaxy_update_volunteers'),
    path('volunteer/<str:pk>', sa_views.volunteer_page, name='volunteer_page'),
    path('edit_volunteer/<str:pk>', sa_views.edit_volunteer, name='edit_volunteer'),
    path('send_survey/', sa_views.send_survey, name='send_survey'),
    path('pre_send_survey/', sa_views.pre_send_survey, name='pre_send_survey'),
    path('survey_page/', sa_views.survey_page, name='survey_page'),
    path('view_availability/<str:pk>', sa_views.view_availability, name='view_availability'),
    path('vol_already_selected/', sa_views.vol_already_selected, name='vol_already_selected'),
    path('view_appointments/', sa_views.view_appointments, name='view_appointments'),
]
