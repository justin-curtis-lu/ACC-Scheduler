
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SeniorForm, VolunteerForm
from .models import Senior, Volunteer, Appointment
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from twilio.rest import Client
from django.db.models import Q
from .methods import check_time
from .methods import check_age
from django.conf import settings
from .methods import get_day
import requests
from requests.auth import HTTPBasicAuth




def home(response):
    """View for the home page"""
    # print(settings.MONKEY_AUTH)
    # print(settings.SURVEY_AUTH)
    return render(response, "scheduling_application/home.html", {})


def console(request):
    """View for console page (home page when logged in)"""
    if not request.user.is_authenticated:
        # Pass Flash message ( You must be authenticated to access this page )
        return render(request, 'scheduling_application/home.html', {})
    return render(request, 'scheduling_application/console.html', {})

# need to place code in console view to automate
def update_volunteers(request):
    if request.GET.get("update_volunteers"):
        print("UPDATING VOLUNTEERS")
        url = 'https://api2.galaxydigital.com/volunteer/user/list/'
        headers = {'Accept': 'scheduling_application/json'}
        params = {'key': settings.GALAXY_AUTH, 'return[]': ["tags", "extras"]}
        response = requests.get(url, headers=headers, params=params)
        voldata = response.json()
        #print(voldata)

        check_list = Volunteer.objects.values_list('galaxy_id', flat=True)
        #print(check_list)

        for i in voldata['data']:
            galaxy_id = int(i['id'])
            if galaxy_id in check_list:
                # update
                volunteer = Volunteer.objects.filter(galaxy_id=galaxy_id)
                try:
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'], additional_notes=i['extras']['availability-context'])
                    if 'Email' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_email=True)
                    if 'Text Message' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_text=True)
                    if 'Phone Call' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_call=True)
                    print("try updaing", volunteer)
                except KeyError:
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'])
                    print("except updating", volunteer)
            else:
                # create
                Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'])
                print("creating", i['firstName'], i['lastName'])


    return redirect('console')
    #return render(request, 'scheduling_application/console.html', {})


def login(request):
    """View for the login page"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('console')
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

    print(seniors_list)

    context = {
        'seniors_list': seniors_list[:5],
        'volunteers_list': volunteers_list[:5],
        'appointments_list': appointments_list
    }

    # Handle scheduling appointment
    if request.method == 'POST':
        senior = request.POST['senior']
        start_address = request.POST['start_address']
        end_address = request.POST['end_address']
        # print(senior)
        # print(request.POST)
        senior_id = Senior.objects.get(id=senior)
        day_time = request.POST['day_time'].split()
        day_of_week = get_day(day_time[0])[:3]
        # print("CHECK: " + day_of_week)
        # print(day_time)
        check_list = Volunteer.objects.filter(Q(availability__has_key=day_of_week)).values()
        #appointment.date_and_time = day_time[0] + " " + day_time[1]
        #appointment.save()
        potential_list = []
        for volunteer in check_list:
            time_list = volunteer['availability'][day_of_week]
            for time in time_list:
                if check_time(day_time[1], time):
                    potential_list.append(volunteer)
                    break

        if len(potential_list) == 0:
            messages.error(request, "No volunteers are available at this time.")
            return redirect('make_appointment')

        appointment = Appointment.objects.create(senior=senior_id, start_address=start_address, end_address=end_address, date_and_time=day_time[0] + " " + day_time[1])

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
    print(potential_list)
    emails_sent = False

    #### MAYBE REMOVE THIS AND FIX ON CONFIRM_V.HTML
    #available_volunteer_list = []
    #for i in potential_list:
    #    if i['dob'] != 'N/A' and check_age(i['dob']):
    #        available_volunteer_list.append(i['first_name'] + " " + i['last_name'] + "(minor)")
    #    else:
    #        available_volunteer_list.append(i['first_name'] + " " + i['last_name'])

    context = {
        'potential_list': potential_list
    }

    if request.method == 'POST':
        selected_volunteers = request.POST
        # print("selected_volunteers", selected_volunteers)
        # print("selected_volunteers volunteer", selected_volunteers.getlist('volunteer'))

        domain = get_current_site(request).domain

        for i in potential_list:
            # print("i", i)
            if str(i['id']) in selected_volunteers.getlist('volunteer'):
                # print("id in selected volunteers", str(i['id']))
                if i['notify_email'] == True:
                    # print("i[notify-email=true]", i)
                    token = get_random_string(length=32)
                    activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i['email'] + "&token=" + token
                    email_subject = 'Appointment Confirmation Email'
                    email_message = 'Click the link below to confirm your availability and attendance of this appointment: ' + activate_url
                    from_email = 'acc.scheduler.care@gmail.com'
                    to_email = [i['email']]
                    send_mail(email_subject, email_message, from_email, to_email)
                    print("to email", to_email)
                    emails_sent = True
                if i['notify_text'] == True:
                    token = get_random_string(length=32)
                    activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i['email'] + "&token=" + token        # MAYBE CAN REMOVE EMAIL QUERY

                    account_sid = 'AC7b1313ed703f0e2697c57e0c1ec641cd'
                    auth_token = '3e77ae49deeeb026e625ea93bd5a3214'
                    client = Client(account_sid, auth_token)

                    message = client.messages.create(body=f'Click the link below to confirm your availability and attendance of this appointment: {activate_url}', from_='+17608218017', to=i['phone'])
                    print("to phone", i['phone'])
                    emails_sent = True

        if emails_sent == True:
            messages.success(request, "Emails/texts sent successfully!")
            return redirect('confirm_v')

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
            appointment = Appointment.objects.filter(id=request.session['appointment'], volunteer=None).update(volunteer=volunteer)
            print("appointment", appointment)

            # print("appointment: ", appointment)
        except (KeyError, Appointment.DoesNotExist):
            # print("APPOINTMENT DOES NOT EXIST")
            appointment = None
        print(appointment)
        return render(request, "scheduling_application/success.html", {})

def send_survey(request):
    if request.GET.get('send_survey'):
        domain = get_current_site(request).domain
        for i in Volunteer.objects.all():
            if i.notify_email == True:
                # print("i[notify-email=true]", i)
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&email=" + i.email + "&token=" + token
                email_subject = 'Availability Survey Email'
                email_message = "Click the link below to select next month's availabilities: " + activate_url
                from_email = 'acc.scheduler.care@gmail.com'
                to_email = [i.email]
                send_mail(email_subject, email_message, from_email, to_email)
                print("to email", to_email)
                emails_sent = True
            if i.notify_text == True:
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&email=" + i.email + "&token=" + token  # MAYBE CAN REMOVE EMAIL QUERY

                account_sid = 'AC7b1313ed703f0e2697c57e0c1ec641cd'
                auth_token = '3e77ae49deeeb026e625ea93bd5a3214'
                client = Client(account_sid, auth_token)

                message = client.messages.create(
                    body=f"Click the link below to select next month's availabilities:  {activate_url}",
                    from_='+17608218017', to=i.phone)
                print("to phone", i.phone)
    return redirect('console')


def survey_page(request):
    if request.method == 'GET':
        vol_id = request.GET.get('id')
        vol_email = request.GET.get('email')
        vol_token = request.GET.get('token')

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
    """View for adding senior"""
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

def update_senior(request):
    """View for updating senior"""
    form = SeniorForm()
    if request.POST.get("update_senior"):
        print("HERE")
        form = SeniorForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('senior_page')
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/update_senior.html', context)

def senior_page(request, pk):
    """View for senior profile page"""
    senior = Senior.objects.get(id=pk)
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("remove_senior"):
            senior.delete()
            return redirect('view_seniors')
        elif request.POST.get("update_senior"):
            print("AYAY")
            return redirect('update_senior')
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

def add_volunteer(request):
    """View for adding volunteer page"""
    form = VolunteerForm()
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('view_volunteers')
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/add_volunteer.html', context)

def volunteer_page(request, pk):
    """View for volunteer profile page"""
    volunteer = Volunteer.objects.get(id=pk)
    if request.method == 'POST':
        volunteer.delete()
        return redirect('view_volunteers')
    context = {
        'volunteer': volunteer,
    }
    return render(request, 'scheduling_application/volunteer_page.html', context)