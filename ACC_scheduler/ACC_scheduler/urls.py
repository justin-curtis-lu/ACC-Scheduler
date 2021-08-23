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
    path('login/', sa_views.login, name='login'),
    path('logout/', sa_views.logout, name='logout'),
    path('success/', sa_views.success, name='confirmation_received'),
    path('make_appointment/', sa_views.make_appointment, name='make_appointment'),
    path('confirm_v', sa_views.confirm_v, name='confirm_v'),
    path('view_seniors/', sa_views.view_seniors, name='view_seniors'),
    path('add_senior/', sa_views.add_senior, name='add_senior'),
    path('senior/<str:pk>', sa_views.senior_page, name='senior_page'),
    path('view_volunteers/', sa_views.view_volunteers, name='view_volunteers'),
    path('update_volunteers/', sa_views.update_volunteers, name='update_volunteers'),
    path('survey/', sa_views.survey, name='survey'),
    # path('activate/<uidb64>/<token>', sa_views.activate, name='activate'),
]
