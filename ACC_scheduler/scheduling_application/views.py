from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Senior, Volunteer, Appointment
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail

potential_list = []

# Create your views here.
def main(response):
    return render(response, "scheduling_application/home.html", {})


def login(request):                                                     # created own login form
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'invalid credentials')
            return redirect('login')                 # TEMPORARY
    return render(request, 'scheduling_application/login.html', {})


def register(request):                                                  # uses Django's built-in UserRegisterForm
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # messages.success(request, f'Account created for {username}.')         # resume tutorial for message display on main page
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'scheduling_application/register.html', {'form': form})


def success(response):
    return render(response, "scheduling_application/success.html", {})


def appointment(request):
    seniors_list = Senior.objects.all()
    volunteers_list = Volunteer.objects.all()
    appointments_list = Appointment.objects.all()

    context = {
        'seniors_list': seniors_list,
        'volunteers_list': volunteers_list,
        'appointments_list': appointments_list
    }

    # Handle scheduling appointment
    potential_list = []
    if 'select_senior' in request.POST:
        senior = request.POST['senior']
        day = request.POST['day']
        potential_list = Volunteer.objects.filter(day=day)
        context = {
            'seniors_list': seniors_list,
            'volunteers_list': volunteers_list,
            'potential_list': potential_list,
            'appointments_list': appointments_list
        }
    if 'select_volunteers' in request.POST:
        email_subject = 'TEMPORARY SUBJECT'
        email_message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam.'
        from_email = 'yeon@uci.edu'
        to_email = [i for i in potential_list if i.checked == "True"]
        send_mail(email_subject, email_message, from_email, to_email)
        # Return flash message "Emails sucessfully sent"
    print("potential list", potential_list)
    return render(request, 'scheduling_application/appointment.html', context)


def index(request):
    return render(request, 'scheduling_application/index.html', {})


def logout(request):
    auth.logout(request)
    return redirect('main')

def view_seniors(request):
    seniors = Senior.objects.all()
    context = {
        'seniors': seniors,
    }
    return render(request, 'scheduling_application/view_seniors.html', context)

def senior_profile(request, id):
    person = Senior