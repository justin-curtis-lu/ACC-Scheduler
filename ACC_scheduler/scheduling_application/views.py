
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from .forms import SeniorForm
from .models import Senior, Volunteer, Appointment
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from twilio.rest import Client



def home(response):
    """View for the home page"""
    return render(response, "scheduling_application/home.html", {})


def login(request):
    """View for the login page"""
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


# uses Django's built-in UserRegisterForm
def register(request):
    """View for the registration page"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}.')         # resume tutorial for message display on main page
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'scheduling_application/register.html', {'form': form})



def make_appointment(request):
    """View for the page where users can schedule an appointment.
       Shows current seniors, volunteers, and appointments.
       Allows users to choose a senior and day then continue."""
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
        senior_id = request.POST['senior']
        senior = Senior.objects.get(id=senior_id)
        day = request.POST['day']
        # print("SENIORS LIST:", seniors_list)
        #for i in Senior.objects.all():
        #    print(i.id)
        # print(senior)
        appointment = Appointment.objects.create(senior=senior)
        potential_list = Volunteer.objects.filter(day=day).values()         # get only volunteers' first and last name
        context = {
            'seniors_list': seniors_list,
            'volunteers_list': volunteers_list,
            'potential_list': potential_list,
            'appointments_list': appointments_list
        }
        request.session['appointment'] = appointment.id
        # print(request.session['appointment'])
        request.session['potential_list'] = list(potential_list)
        return redirect('confirm_v')
    return render(request, 'scheduling_application/make_appointment.html', context)



def confirm_v(request):
    """View for page to confirm which volunteers to send emails to."""
    potential_list = request.session['potential_list']
    # print(potential_list)


    context = {
        'potential_list': potential_list
    }

    if request.method == 'POST':
        selected_volunteers = request.POST
        print("selected_volunteers", selected_volunteers)

        domain = get_current_site(request).domain

        for i in potential_list:
            if str(i['id']) in selected_volunteers['volunteer']:
                if i['notif_email'] == True:
                    token = get_random_string(length=32)
                    activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i['email'] + "&token=" + token
                    email_subject = 'Appointment Confirmation Email'
                    email_message = 'Click the link below to confirm your availability and attendance of this appointment: ' + activate_url
                    from_email = 'acc.scheduler.care@gmail.com'
                    to_email = [i['email']]
                    send_mail(email_subject, email_message, from_email, to_email)
                    # print("to email", to_email)
                if i['notif_text'] == True:
                    token = get_random_string(length=32)
                    activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i['email'] + "&token=" + token        # MAYBE CAN REMOVE EMAIL QUERY

                    account_sid = 'AC7b1313ed703f0e2697c57e0c1ec641cd'
                    auth_token = '3e77ae49deeeb026e625ea93bd5a3214'
                    client = Client(account_sid, auth_token)

                    message = client.messages.create(body=f'Click the link below to confirm your availability and attendance of this appointment: {activate_url}', from_='+17608218017', to='+16504848988')

        # request.session['selected_volunteers'] = request.POST.getlist('volunteer')
        # print("session selected volunteers", request.session['selected_volunteers'])
        # messages.success(request, 'Emails successfully sent')
    return render(request, 'scheduling_application/confirm_v.html', context)


# Currently not using email and token queries
def success(request):
    """View for the email sending success page"""
    if request.method == 'GET':
        vol_id = request.GET.get('id')
        vol_email = request.GET.get('email')
        vol_token = request.GET.get('token')

        try:
            volunteer = Volunteer.objects.get(id=vol_id)
            # print(volunteer, type(volunteer))
            appointment = Appointment.objects.filter(id=request.session['appointment']).update(volunteer=volunteer)
            # print("appointment: ", appointment)
        except (KeyError, Appointment.DoesNotExist):
            # print("APPOINTMENT DOES NOT EXIST")
            appointment = None
        print(appointment)
        return render(request, "scheduling_application/success.html", {})




def index(request):
    """View for index page (home page when logged in)"""
    return render(request, 'scheduling_application/index.html', {})


def logout(request):
    """View for logging out"""
    auth.logout(request)
    return redirect('home')


def view_seniors(request):
    """View for the seniors page (table of all the seniors in the database)"""
    seniors = Senior.objects.all()
    context = {
        'seniors': seniors,
    }
    return render(request, 'scheduling_application/view_seniors.html', context)

def add_senior(request):
    """View for adding senior page"""
    form = SeniorForm()
    if request.method == 'POST':
        form = SeniorForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('view_seniors')
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/add_senior.html', context)

def senior_page(request, pk):
    """View for senior profile page"""
    senior = Senior.objects.get(id=pk)
    if request.method == 'POST':
        senior.delete()
        return redirect('view_seniors')
    context = {
        'senior': senior,
    }
    #print(senior.id)
    return render(request, 'scheduling_application/senior_page.html', context)

def view_volunteers(request):
    """View for the volunteers page (table of all the volunteers in the database)"""
    volunteers = Volunteer.objects.all()
    context = {
        'volunteers': volunteers,
    }
    return render(request, 'scheduling_application/view_volunteers.html', context)
