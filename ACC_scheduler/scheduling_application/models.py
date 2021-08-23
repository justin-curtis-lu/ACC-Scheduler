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

class Day(models.Model):
    _9_10 = models.BooleanField(default=False)
    _10_11 = models.BooleanField(default=False)
    _11_12 = models.BooleanField(default=False)
    _12_1 = models.BooleanField(default=False)
    _1_2 = models.BooleanField(default=False)
    all = models.BooleanField(default=False)

class Availability(models.Model):
    _1 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _2 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _3 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _4 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _5 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _6 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _7 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _8 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _9 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _10 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _11 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _12 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _13 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _14 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _15 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _16 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _17 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _18 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _19 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _20 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _21 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _22 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _23 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _24 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _25 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _26 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _27 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _28 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _29 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _30 = models.ForeignKey(Day, on_delete=models.CASCADE)
    _31 = models.ForeignKey(Day, on_delete=models.CASCADE)

# Subject to change based on data we can get from Galaxy Digital
class Volunteer(models.Model):
    """Model for all the volunteers in the database"""
    galaxy_id = models.IntegerField(default=None, null=True)
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    phone = models.CharField(default=None, max_length=30, null=True)
    email = models.CharField(max_length=40, default='None')
    # age = models.IntegerField(default=0)
    # address?
    dob = models.CharField(max_length=10, default=None, null=True)
    vaccinated = models.BooleanField(default=False)
    notify_email = models.BooleanField(default=False)
    notify_text = models.BooleanField(default=False)
    notify_call = models.BooleanField(default=False)
    availability = models.ForeignKey(Availability, on_delete=models.CASCADE)
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
