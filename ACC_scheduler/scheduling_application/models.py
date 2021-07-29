from django.db import models

# Create your models here.
class Senior(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    age = models.IntegerField(default=0)
    address = models.TextField(default="N/A")
    vaccinated = models.BooleanField(default=False)


