from django.db import models


class Senior(models.Model):
    """Models for all the seniors in the database"""
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    # age = models.IntegerField(default=0)
    address = models.CharField(default='N/A', max_length=100)
    phone = models.CharField(default='N/A', max_length=30)
    email = models.CharField(max_length=40, default='None')
    emergency_contacts = models.CharField(default='N/A', max_length=100)
    preferred_language = models.CharField(default='N/A', max_length=100)
    additional_notes = models.TextField(default='N/A')
    vaccinated = models.BooleanField(default=None)
    notify_email = models.BooleanField(default=None)
    notify_text = models.BooleanField(default=None)
    notify_call = models.BooleanField(default=None)

    def __str__(self):
        return self.full_name


# Subject to change based on data we can get from Galaxy Digital
class Volunteer(models.Model):
    """Model for all the volunteers in the database"""
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    phone = models.CharField(default='N/A', max_length=30)
    email = models.CharField(max_length=40, default='None')
    #age = models.IntegerField(default=0)
    dob = models.CharField(max_length=10, default='N/A')
    vaccinated = models.BooleanField(default=None)
    notify_email = models.BooleanField(default=None)
    notify_text = models.BooleanField(default=None)
    notify_call = models.BooleanField(default=None)
    availability = models.JSONField(default=dict)
    current_appointments = models.JSONField(default=dict, editable=False)
    additional_notes = models.TextField(default='N/A')

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    """Model for the appointments"""
    senior = models.ForeignKey(Senior, default=0, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, null=True)
    location = models.CharField(max_length=50)
    date_and_time = models.DateTimeField(auto_now_add=True)
    purpose_of_trip = models.TextField(default="N/A")
    notes = models.TextField(default="N/A")
    # Add a Status field (Waiting for confirmation, Confirmed <- should be triggered by the clicked link)

    @property
    def details(self):
        return '%s %s %s' % (self.senior, self.volunteer, self.date_and_time)

    def __str__(self):
        return self.details
