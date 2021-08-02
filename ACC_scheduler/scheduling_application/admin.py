from django.contrib import admin
from django.contrib.auth.models import Group
from scheduling_application.models import Senior, Volunteer, Appointment

# Register your models here.

@admin.register(Senior)
class SeniorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "address", "vaccinated")


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "vaccinated")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("senior", "location", "date_and_time", "notes")


admin.site.site_header = "Scheduling Application Admin Page"
admin.site.unregister(Group)