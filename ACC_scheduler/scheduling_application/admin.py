from django.contrib import admin
from scheduling_application.models import Senior

# Register your models here.
@admin.register(Senior)
class SeniorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "age", "vaccinated")
