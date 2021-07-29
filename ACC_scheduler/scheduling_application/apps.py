from django.apps import AppConfig


class SchedulingApplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduling_application'

    # changes the header name on the admin site
    verbose_name = 'Users Database'         # MAY NEED TO CHANGE IF USED ELSEWHERE
