
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from .forms import SeniorForm
from .models import Senior, Volunteer, Appointment, Day
from django.contrib.auth.models import User, auth
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from twilio.rest import Client
from django.db.models import Q
from .methods import check_time, check_age, get_day, get_timeframes
from django.conf import settings
import requests
from requests.auth import HTTPBasicAuth




def home(response):
    """View for the home page"""
    # print(settings.MONKEY_AUTH)
    # print(settings.SURVEY_AUTH)

    # volunteer = Volunteer.objects.get(id=1)
    # volunteer2 = Volunteer.objects.get(id=2)
    # print(volunteer.Days.all())
    # volunteer.Days.filter(volunteer=volunteer).delete()
    # volunteer2.Days.filter(volunteer=volunteer2).delete()
    # print(volunteer.Days.all())
    # print(volunteer2.Days.all())

    # day_object = volunteer.Days.filter(day_of_month=1)
    # day_object.update(_10_11=True)
    # print(day_object.first()._10_11)
    #print(volunteers_list.Days.filter(day_of_month=7))
    #volunteers_list.Days.filter(volunteer=volunteers_list).delete()
    #print(volunteers_list.Days.all())
    return render(response, "scheduling_application/home.html", {})


def console(request):
    """View for console page (home page when logged in)"""
    if not request.user.is_authenticated:
        # Pass Flash message ( You must be authenticated to access this page )
        return render(request, 'scheduling_application/home.html', {})
    #check_list = Volunteer.objects.values_list('galaxy_id', flat=True)
    #if 4032242 in check_list:
    #    print("yes")
    #print("CHECK_LIST", check_list)

    # volunteer = Volunteer.objects.get(last_name="tong")
    # volunteer2 = Volunteer.objects.get(last_name="vol")
    # Day.objects.create(_9_10=True, day_of_month=1, volunteer=volunteer)
    # Day.objects.create(_9_10=True, _10_11=True, _11_12=True, _12_1=True, _1_2=True, day_of_month=1, volunteer=volunteer2)

    #volunteers_list[0].availability = test
    #print(volunteers_list[0].availability)
    return render(request, 'scheduling_application/console.html', {})


def update_volunteers(request):
    if request.GET.get("update_volunteers"):
        print("UPDATING VOLUNTEERS")
        url = 'https://api2.galaxydigital.com/volunteer/user/list/'
        headers = {'Accept': 'scheduling_application/json'}
        params = {'key': settings.GALAXY_AUTH}
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
                volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'])
                print("updating", volunteer)
            else:
                # create
                Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'])
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

    # print(seniors_list)
    # print("BELOW")
    # print(volunteers_list[0].Appointments.all())
    # print(volunteers_list[1].Appointments.all())

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
        senior_id = Senior.objects.get(id=senior)
        day_time = request.POST['day_time'].split()
        day_of_month = int(day_time[0].split('/')[1])
        check_list = Day.objects.filter(day_of_month=day_of_month).values_list("volunteer", flat=True)
        potential_list = []
        for volunteer in check_list:
            volunteer_object = Volunteer.objects.filter(id=volunteer)
            availability = volunteer_object[0].Days.filter(day_of_month=day_of_month)[0]
            if availability.all:
                potential_list.append(volunteer_object.values()[0])
            else:
                time_frames = get_timeframes([availability._9_10, availability._10_11, availability._11_12, availability._12_1, availability._1_2])
                for time in time_frames:
                    if check_time(day_time[1], time):
                        check_conflict = volunteer_object[0].Appointments.filter(date_and_time__contains=day_time[0])
                        break_check = False
                        for appointment in check_conflict:
                            if check_time(day_time[1], appointment.date_and_time.split(' ')[1]):
                                break_check = True
                                break
                        if break_check:
                            break
                        volunteer_object[0].Appointments.filter()
                        potential_list.append(volunteer_object.values()[0])
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
            #appointment_object = Appointment.objects.get(id=request.session['appointment'])
            #appointment_day_time = appointment_object.date_and_time.split(' ')
            #volunteer.current_appointments[appointment_day_time[0]] = appointment_day_time[1]
            #volunteer.save()
            # print("appointment", appointment)

            # print("appointment: ", appointment)
        except (KeyError, Appointment.DoesNotExist):
            # print("APPOINTMENT DOES NOT EXIST")
            appointment = None
        # print(appointment)
        return render(request, "scheduling_application/success.html", {})


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
