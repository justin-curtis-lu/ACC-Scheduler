from django.shortcuts import render, redirect
# from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Senior, Volunteer, Appointment
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail


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
    if request.method == 'POST':
        senior = request.POST['senior']
        day = request.POST['day']
        potential_list = Volunteer.objects.filter(day=day).values()         # get only volunteers' first and last name
        context = {
            'seniors_list': seniors_list,
            'volunteers_list': volunteers_list,
            'potential_list': potential_list,
            'appointments_list': appointments_list
        }
        request.session['potential_list'] = list(potential_list)
        return redirect('appointment_pt2')
    return render(request, 'scheduling_application/appointment.html', context)

def appointment_pt2(request):
    potential_list = request.session['potential_list']
    print(potential_list)
    available_volunteer_list = []
    for i in potential_list:
        available_volunteer_list.append(i['first_name'] + " " + i['last_name'])

    context = {
        'available_volunteer_list': available_volunteer_list
        #'potential_list': potential_list
    }
    if request.method == 'POST':
        selected_volunteers = request.POST.getlist('volunteer')
        print(selected_volunteers)
        email_subject = 'TEMPORARY SUBJECT'
        email_message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer nec odio. Praesent libero. Sed cursus ante dapibus diam.'
        from_email = 'yeon@uci.edu'
        to_email = [i['email'] for i in potential_list if potential_list[0]['first_name'] in selected_volunteers]
        send_mail(email_subject, email_message, from_email, to_email)
        print(to_email)
        # Return flash message "Emails sucessfully sent"
    print("available_volunteer_list", available_volunteer_list)
    return render(request, 'scheduling_application/appointment_pt2.html', context)


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