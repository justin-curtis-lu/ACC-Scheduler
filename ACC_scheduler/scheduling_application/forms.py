from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from .models import Senior, Volunteer, Day, Appointment


class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)


class KeyForm(forms.Form):
    key1 = forms.CharField(label='key1', max_length=100)
    key2 = forms.CharField(label='key2', max_length=100)
    key3 = forms.CharField(label='key3', max_length=100)


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