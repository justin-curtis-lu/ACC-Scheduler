from django.db import models


class Senior(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    age = models.IntegerField(default=0)
    address = models.TextField(default="N/A")
    vaccinated = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Volunteer(models.Model):
    last_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)

    @property
    def full_name(self):
        return '%s %s' % (self.first_name, self.last_name)

    vaccinated = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class Appointment(models.Model):
    senior = models.ForeignKey(Senior, default=0, on_delete=models.CASCADE)         # number in default value is equal to number in senior database
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    location = models.CharField(max_length=50)
    date_and_time = models.DateTimeField()
    purpose_of_trip = models.TextField(default="N/A")
    notes = models.TextField(default="N/A")

    @property
    def details(self):
        return '%s %s %s' % (self.senior, self.volunteer, self.date_and_time)

    def __str__(self):
        return self.details
