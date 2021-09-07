from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Senior, Volunteer, Day, Appointment


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class SeniorForm(ModelForm):
    class Meta:
        model = Senior
        fields = '__all__'


class VolunteerForm(ModelForm):
    class Meta:
        model = Volunteer
        fields = '__all__'
        exclude = ['galaxy_id', 'survey_token']


class DayForm(ModelForm):
    class Meta:
        model = Day
        fields = '__all__'
        exclude = ['volunteer', 'day_of_month']


class AppointmentForm(ModelForm):
    class Meta:
        model = Appointment
        fields = '__all__'
        exclude = ['id']