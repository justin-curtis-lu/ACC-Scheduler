from django.db import models


class Senior(models.Model):
    """Models for all the seniors in the database"""
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

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
    galaxy_id = models.IntegerField(default=None, null=True)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    phone = models.CharField(default=None, max_length=30, null=True)
    email = models.CharField(max_length=40, default='None')
    address = models.CharField(default='N/A', max_length=100)
    dob = models.CharField(max_length=10, default=None, null=True)
    minor = models.BooleanField(default=False, editable=False)
    vaccinated = models.BooleanField(default=False)
    notify_email = models.BooleanField(default=False)
    notify_text = models.BooleanField(default=False)
    notify_call = models.BooleanField(default=False)
    additional_notes = models.TextField(default=None, null=True, blank=True)
    survey_token = models.CharField(default=None, max_length=32, null=True, blank=True)
    unsubscribed = models.BooleanField(default=False)

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.notify_email and not self.notify_text and not self.notify_call:
            raise ValidationError('At least one notification method must be selected')

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def __str__(self):
        return self.full_name


class Day(models.Model):
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, related_name="Days", blank=True, null=True)
    date = models.CharField(default=None, max_length=10, null=True)
    _9_10 = models.BooleanField(default=False)
    _10_11 = models.BooleanField(default=False)
    _11_12 = models.BooleanField(default=False)
    _12_1 = models.BooleanField(default=False)
    _1_2 = models.BooleanField(default=False)
    all = models.BooleanField(default=False)


class SurveyStatus(models.Model):
    month = models.IntegerField(null=True)
    year = models.IntegerField(null=True)
    sent = models.BooleanField(default=False)
    survey_id = models.IntegerField(null=True)


class Appointment(models.Model):
    """Model for the appointments"""
    senior = models.ForeignKey(Senior, default=0, on_delete=models.CASCADE)
    # volunteer = models.ManyToManyField(Volunteer, related_name="Appointments")
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE, null=True, related_name="Appointments")
    start_address = models.CharField(max_length=50, null=True)
    end_address = models.CharField(max_length=50, null=True)
    date_and_time = models.CharField(max_length=50)
    purpose_of_trip = models.TextField(default="N/A")
    notes = models.TextField(default="N/A")
    # Add a Status field (Waiting for confirmation, Confirmed <- should be triggered by the clicked link)

    @property
    def details(self):
        return '%s %s %s' % (self.senior, self.volunteer, self.date_and_time)

    def __str__(self):
        return self.details
