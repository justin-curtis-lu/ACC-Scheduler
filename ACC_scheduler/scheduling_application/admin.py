from django.contrib import admin
from django.contrib.auth.models import Group
from scheduling_application.models import Senior

# Register your models here.

@admin.register(Senior)
class SeniorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "age", "vaccinated")

admin.site.site_header = "Scheduling Application Admin Page"
admin.site.unregister(Group)