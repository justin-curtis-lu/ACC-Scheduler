
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SeniorForm, VolunteerForm
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
from django.forms.models import model_to_dict
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

# need to place code in console view to automate
def galaxy_update_volunteers(request):
    if request.GET.get("galaxy_update_volunteers"):
        print("UPDATING VOLUNTEERS")
        url = 'https://api2.galaxydigital.com/volunteer/user/list/'
        headers = {'Accept': 'scheduling_application/json'}
        params = {'key': settings.GALAXY_AUTH, 'return[]': "extras"}
        response = requests.get(url, headers=headers, params=params)
        voldata = response.json()
        print(voldata)

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
                    print("try updating", volunteer)
                except KeyError:
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'])
                    print("except updating", volunteer)
            else:
                # create
                try:
                    Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'], additional_notes=i['extras']['availability-context'])
                    if 'Email' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_email=True)
                    if 'Text Message' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_text=True)
                    if 'Phone Call' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_call=True)
                    print("try creating", i['firstName'], i['lastName'])
                except KeyError:
                    Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                             phone=i['phone'], email=i['email'], dob=i['birthdate'])
                    print("except creating", i['firstName'], i['lastName'])


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
        # day_of_week = get_day(day_time[0])[:3]
        day_of_month = int(day_time[0].split('/')[1])
        # print("CHECK: " + day_of_week)
        # print(day_time)
        check_list = Day.objects.filter(day_of_month=day_of_month).values_list("volunteer", flat=True)
        # check_list is a queryset of volunteer ids
        print(check_list)
        print("ABOVE")
        #appointment.date_and_time = day_time[0] + " " + day_time[1]
        #appointment.save()
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
                        potential_list.append(volunteer_object.values()[0])
                        break
            # time_list = volunteer['availability'][day_of_week]
            # SEARCH THROUGH DAY OBJECT AND GET THE TIMES AVAILABLE
            # For each day and time a volunteer is available
            #for time in time_list:
                # if there is an available time that fits
            #    if check_time(day_time[1], time):
                    # checks if volunteer already has an appointment at that day if not, the volunteer is available
            #        check_conflict = volunteer['current_appointments']
            #        if day_time[0] in check_conflict:
            #            break
            #        potential_list.append(volunteer)
            #        break

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
        appointment = Appointment.objects.filter(id=request.session['appointment'], volunteer=None).values()
        print(appointment)
        print(appointment[0]['senior_id'])
        senior = Senior.objects.filter(id=appointment[0]['senior_id']).values()
        print(senior)

        for i in potential_list:
            # print("i", i)
            if str(i['id']) in selected_volunteers.getlist('volunteer'):
                # print("id in selected volunteers", str(i['id']))
                if i['notify_email'] == True:
                    # print("i[notify-email=true]", i)
                    token = get_random_string(length=32)
                    activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i['email'] + "&token=" + token
                    email_subject = 'Volunteer Appointment Confirmation'
                    email_message = f'Hello Volunteer!\n\nWe have a Senior Escort Program Participant who requests a buddy! Based on your availability, you would be a perfect match!\n' + \
                                    f'\tWho: {senior[0]["first_name"]} {senior[0]["last_name"]}\n' \
                                    f'\tWhat: {appointment[0]["purpose_of_trip"]}\n' \
                                    f'\tWhen: {appointment[0]["date_and_time"]}\n' \
                                    f'\tWhere: {appointment[0]["start_address"]} to {appointment[0]["end_address"]}\n' + \
                                    'Please click the link below to accept this request.\n' + activate_url + \
                                    '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff'
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

                    message = client.messages.create(body=f'Hello Volunteer!\n\nWe have a Senior Escort Program Participant who requests a buddy! Based on your availability, you would be a perfect match!\n' + \
                                                          f'\tWho: {senior[0]["first_name"]} {senior[0]["last_name"]}\n' \
                                                          f'\tWhat: {appointment[0]["purpose_of_trip"]}\n' \
                                                          f'\tWhen: {appointment[0]["date_and_time"]}\n' \
                                                          f'\tWhere: {appointment[0]["start_address"]} to {appointment[0]["end_address"]}\n' + \
                                                          'Please click the link below to accept this request.\n' + activate_url + \
                                                          '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff',
                                                          from_='+17608218017', to=i['phone'])
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

            empty_appointment = Appointment.objects.filter(id=request.session['appointment'], volunteer=None)
            if not empty_appointment:
                return redirect('vol_already_selected')
            empty_appointment.update(volunteer=volunteer)
            appointment = Appointment.objects.get(id=request.session['appointment'])
            print(appointment)
            appointment_day_time = appointment.date_and_time.split(' ')
            volunteer.current_appointments[appointment_day_time[0]] = appointment_day_time[1]
            volunteer.save()
            # print("appointment", appointment)
        except (KeyError, Appointment.DoesNotExist):
            # print("APPOINTMENT DOES NOT EXIST")
            appointment = None
        context = {
            'appointment': appointment
        }
        # print(appointment)
        return render(request, "scheduling_application/success.html", context)

def vol_already_selected(request):
    return render(request, "scheduling_application/vol_already_selected.html", {})


def send_survey(request):
    if request.GET.get('send_survey'):
        domain = get_current_site(request).domain
        for i in Volunteer.objects.all():
            if i.notify_email == True:
                # print("i[notify-email=true]", i)
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&email=" + i.email + "&token=" + token
                email_subject = 'Volunteer Availability Survey'
                email_message = "Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                                "Your time is so appreciated and we could not provide seniors with free programs without you!\n" + activate_url + "\n\nSincerely,\nSenior Escort Program Staff"
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
                    body="Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                          f"Your time is so appreciated and we could not provide seniors with free programs without you!\n{activate_url}\n\nSincerely,\nSenior Escort Program Staff",
                    from_='+17608218017', to=i.phone)
                print("to phone", i.phone)
    return redirect('console')


def survey_page(request):
    if request.method == 'GET':
        request.session['vol_id'] = request.GET.get('id')
        request.session['vol_email'] = request.GET.get('email')
        request.session['vol_token'] = request.GET.get('token')

    if request.method == 'POST':
        ### !!!!! MAKE SURE THIS WORKS WITH MULTIPLE USERS AT SAME TIME, ELSE JUST ADD SECTION WHERE THEY PUT IN EMAIL AND STUFF ON FORM (BUT WHAT ABOUT ID?) !!!!!
        vol_id = request.session['vol_id']
        vol_email = request.session['vol_email']
        vol_token = request.session['vol_token']
        option_list = request.POST.getlist('survey-value')
        volunteer = Volunteer.objects.get(id=vol_id)
        volunteer.Days.filter(volunteer=volunteer).delete()

        for i in option_list:
            date = i[6:].split("-")
            if date[1] == "0":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day._9_10 = True
                    day.save()
                except:
                    Day.objects.create(_9_10=True, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                                       day_of_month=date[0], volunteer=volunteer)
            elif date[1] == "1":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day._10_11=True
                    day.save()
                except:
                    Day.objects.create(_9_10=False, _10_11=True, _11_12=False, _12_1=False, _1_2=False, all=False,
                                       day_of_month=date[0], volunteer=volunteer)
            elif date[1] == "2":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day._11_12 = True
                    day.save()
                except:
                    Day.objects.create(_9_10=False, _10_11=False, _11_12=True, _12_1=False, _1_2=False, all=False,
                                       day_of_month=date[0], volunteer=volunteer)
            elif date[1] == "3":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day._12_1 = True
                    day.save()
                except:
                    Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=True, _1_2=False, all=False,
                                       day_of_month=date[0], volunteer=volunteer)
            elif date[1] == "4":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day._1_2 = True
                    day.save()
                except:
                    Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=True, all=False,
                                       day_of_month=date[0], volunteer=volunteer)
            elif date[1] == "5":
                try:
                    day = volunteer.Days.get(day_of_month=date[0])
                    day.all = True
                    day.save()
                except:
                    Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=True,
                                       day_of_month=date[0], volunteer=volunteer)
            # Render a success page
            # return render(request, "scheduling_application/survey_complete.html", {})
        for i in volunteer.Days.all():
            print(model_to_dict(i))
        #print(volunteer.Days.all())
    return render(request, "scheduling_application/survey_page.html", {})


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

def edit_senior(request, pk):
    """View for editing senior"""
    senior = Senior.objects.get(id=pk)
    data = {'last_name': senior.last_name, 'first_name': senior.first_name, 'address': senior.address, 'phone': senior.phone, 'email': senior.email, 'emergency_contacts': senior.emergency_contacts,
            'preferred_language': senior.preferred_language, 'additional_notes': senior.additional_notes, 'vaccinated': senior.vaccinated,
            'notify_email': senior.notify_email, 'notify_text': senior.notify_text, 'notify_call': senior.notify_call}
    form = SeniorForm(initial=data)
    if request.method == 'POST':
        form = SeniorForm(request.POST, instance=senior)
        if form.is_valid():
            form.save()
        return redirect('senior_page', pk)
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/edit_senior.html', context)

def senior_page(request, pk):
    """View for senior profile page"""
    senior = Senior.objects.get(id=pk)
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("remove_senior"):
            senior.delete()
            return redirect('view_seniors')
        elif request.POST.get("edit_senior"):
            return redirect('edit_senior', pk)
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
        print(request.POST)
        if request.POST.get("remove_volunteer"):
            volunteer.delete()
            return redirect('view_volunteers')
        elif request.POST.get("edit_volunteer"):
            return redirect('edit_volunteer', pk)
    context = {
        'volunteer': volunteer,
    }
    return render(request, 'scheduling_application/volunteer_page.html', context)

def edit_volunteer(request, pk):
    """View for editing volunteer"""
    volunteer = Volunteer.objects.get(id=pk)
    data = {'galaxy_id': volunteer.galaxy_id, 'last_name': volunteer.last_name, 'first_name': volunteer.first_name, 'phone': volunteer.phone, 'email': volunteer.email, 'dob': volunteer.dob,
            'vaccinated': volunteer.vaccinated,'notify_email': volunteer.notify_email, 'notify_text': volunteer.notify_text, 'notify_call': volunteer.notify_call,
            'current_appointments': volunteer.current_appointments, 'additional_notes': volunteer.additional_notes}
    form = VolunteerForm(initial=data)
    if request.method == 'POST':
        form = VolunteerForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
        return redirect('volunteer_page', pk)
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/edit_volunteer.html', context)