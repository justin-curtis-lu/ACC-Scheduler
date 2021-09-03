from django.contrib import admin
from django.contrib.auth.models import Group
from scheduling_application.models import Senior, Volunteer, Appointment, Day

# Register your models here.

@admin.register(Senior)
class SeniorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "address", "vaccinated")


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "vaccinated")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("senior", "start_address", "end_address", "date_and_time", "notes")

@admin.register(Day)
class DayAdmin(admin.ModelAdmin):
    list_display = ("_9_10", "_10_11", "_11_12", "_12_1", "_1_2", "all")


admin.site.site_header = "Scheduling Application Admin Page"
admin.site.unregister(Group)