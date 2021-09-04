
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, SeniorForm, VolunteerForm, DayForm, AppointmentForm
from django.forms import modelformset_factory, formset_factory
from .models import Senior, Volunteer, Appointment, Day, SurveyStatus
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
from django.core.paginator import Paginator
from datetime import datetime


def home(response):
    """View for the home page"""
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
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'], address=i['address'], additional_notes=i['extras']['availability-context'])
                    if 'Email' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_email=True)
                    if 'Text Message' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_text=True)
                    if 'Phone Call' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_call=True)
                    print("try updating", volunteer)
                except KeyError:
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'], phone=i['phone'], email=i['email'], dob=i['birthdate'], address=i['address'])
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

def keys(request):
    if request.method == 'POST':
        key1 = request.POST['key1']
        key2 = request.POST['key2']
        key3 = request.POST['key3']
        if key1 == settings.KEY1 and key2 == settings.KEY2 and key3 == settings.KEY3:
            return redirect('register')
        else:
            messages.info(request, 'invalid credentials')
            return render(request, 'scheduling_application/keys.html', {})
    else:
        return render(request, 'scheduling_application/keys.html', {})

def make_appointment(request):
    """View for the page where users can schedule an appointment.
       Shows current seniors, volunteers, and appointments.
       Allows users to choose a senior and day then continue."""
    seniors_list = Senior.objects.all()
    volunteers_list = Volunteer.objects.all()

    context = {
        'seniors_list': seniors_list[:5],
        'volunteers_list': volunteers_list[:5]
    }
    # Handle scheduling appointment
    if request.method == 'POST':
        senior = request.POST['senior']
        start_address = request.POST['start_address']
        end_address = request.POST['end_address']
        purpose_of_trip = request.POST['purpose_of_trip']
        additional_notes = request.POST['notes']
        senior_id = Senior.objects.get(id=senior)
        day_time = request.POST['day_time'].split()
        day_of_month = int(day_time[0].split('/')[1])
        check_list = Day.objects.filter(day_of_month=day_of_month).values_list("volunteer", flat=True)
        potential_list = []
        for volunteer in check_list:
            volunteer_object = Volunteer.objects.filter(id=volunteer)
            availability = volunteer_object[0].Days.filter(day_of_month=day_of_month)[0]
            if availability.all:
                check_conflict = volunteer_object[0].Appointments.filter(date_and_time__contains=day_time[0])
                schedule_conflict = False
                for appointment in check_conflict:
                    if check_time(day_time[1], appointment.date_and_time.split(' ')[1]):
                        schedule_conflict = True
                        break
                if not schedule_conflict:
                   potential_list.append(volunteer_object.values()[0])
                # potential_list.append(volunteer_object.values()[0])
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

        appointment = Appointment.objects.create(senior=senior_id, start_address=start_address, end_address=end_address, date_and_time=day_time[0] + " " + day_time[1], purpose_of_trip=purpose_of_trip, notes=additional_notes)
        context = {
            'seniors_list': seniors_list,
            'volunteers_list': volunteers_list,
            'potential_list': potential_list
        }
        request.session['appointment'] = appointment.id
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

                    account_sid = settings.TWILIO_ACCOUNT_SID
                    auth_token = settings.TWILIO_AUTH
                    client = Client(account_sid, auth_token)

                    message = client.messages.create(body=f'Hello Volunteer!\n\nWe have a Senior Escort Program Participant who requests a buddy! Based on your availability, you would be a perfect match!\n' + \
                                                          f'\tWho: {senior[0]["first_name"]} {senior[0]["last_name"]}\n' \
                                                          f'\tWhat: {appointment[0]["purpose_of_trip"]}\n' \
                                                          f'\tWhen: {appointment[0]["date_and_time"]}\n' \
                                                          f'\tWhere: {appointment[0]["start_address"]} to {appointment[0]["end_address"]}\n' + \
                                                          'Please click the link below to accept this request.\n' + activate_url + \
                                                          '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff',
                                                          from_='+19569486977', to=i['phone'])
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
            # empty_appointment.update(volunteer=volunteer)
            empty_appointment[0].volunteer.add(volunteer)
            appointment = Appointment.objects.get(id=request.session['appointment'])
            print(appointment)

            # SEND EMAIL TO SENIORS
            senior = appointment.senior
            if senior.notify_email == True:
                email_subject = 'Participant Appointment Confirmation'
                email_message = f'Hello Participant!\n\nWe have a Senior Escort Program Volunteer who has accepted your request! Here are the details of the appointment!\n' + \
                                f'\tVolunteer: {volunteer.first_name} {volunteer.last_name}\n' \
                                f'\tWhat: {appointment.purpose_of_trip}\n' \
                                f'\tWhen: {appointment.date_and_time}\n' \
                                f'\tWhere: {appointment.start_address} to {appointment.end_address}\n' + \
                                '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff'
                from_email = 'acc.scheduler.care@gmail.com'
                to_email = [senior.email]
                send_mail(email_subject, email_message, from_email, to_email)
                print("to email", to_email)
                # emails_sent = True
            if senior.notify_text == True:
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH
                client = Client(account_sid, auth_token)

                message = client.messages.create(
                    body=f'Hello Participant!\n\nWe have a Senior Escort Program Volunteer who has accepted your request! Here are the details of the appointment!\n' + \
                         f'\tVolunteer: {volunteer.first_name} {volunteer.last_name}\n' \
                         f'\tWhat: {appointment.purpose_of_trip}\n' \
                         f'\tWhen: {appointment.date_and_time}\n' \
                         f'\tWhere: {appointment.start_address} to {appointment.end_address}\n' + \
                         '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff',
                    from_='+19569486977', to=senior.phone)
                print("to phone", senior.phone)
                # emails_sent = True

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

def pre_send_survey(request):
    return render(request, 'scheduling_application/survey_confirmation.html')

def send_survey(request):
    if request.GET.get('send_survey'):
        dt = datetime.today()
        curr_month = dt.month
        if SurveyStatus.objects.count() == 0:
            survey = SurveyStatus.objects.create(month=curr_month, sent=False, survey_id=1)
        else:
            survey = SurveyStatus.objects.get(survey_id=1)
        if survey.sent is False or survey.month is not curr_month:
            domain = get_current_site(request).domain
            for i in Volunteer.objects.all():
                token = get_random_string(length=32)
                i.survey_token = token
                activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&email=" + i.email \
                               + "&token=" + token
                if i.notify_email:
                    email_subject = 'Volunteer Availability Survey'
                    email_message = "Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                                    "Your time is so appreciated and we could not provide seniors with free programs without you!\n" + activate_url + "\n\nSincerely,\nSenior Escort Program Staff"
                    from_email = 'acc.scheduler.care@gmail.com'
                    to_email = [i.email]
                    send_mail(email_subject, email_message, from_email, to_email)
                    print("to email", to_email)
                    emails_sent = True
                if i.notify_text:
                    account_sid = settings.TWILIO_ACCOUNT_SID
                    auth_token = settings.TWILIO_AUTH
                    client = Client(account_sid, auth_token)
                    message = client.messages.create(
                        body="Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                             f"Your time is so appreciated and we could not provide seniors with free programs without you!\n{activate_url}\n\nSincerely,\nSenior Escort Program Staff",
                        from_='+19569486977', to=i.phone)
                    print("to phone", i.phone)
                i.survey_token = token
                i.save()
                survey.month = curr_month
            survey.sent = True
            survey.save()
            messages.success(request, f'Successfully sent surveys for the month of {curr_month}.')
        else:
            messages.warning(request, f'You have already sent surveys for the month of {curr_month}.')
    return redirect('pre_send_survey')

def survey_page(request):
    if request.method == 'GET':
        request.session['vol_id'] = request.GET.get('id')
        request.session['vol_email'] = request.GET.get('email')
        request.session['vol_token'] = request.GET.get('token')
        vol_id = request.session['vol_id']
        vol_token = request.session['vol_token']
        volunteer = Volunteer.objects.get(id=vol_id)
        current_month = datetime.now().strftime('%m')
        date = {'month': current_month}
        if vol_token != volunteer.survey_token:
            return render(request, "scheduling_application/bad_link.html", {})
        else:
            return render(request, "scheduling_application/survey_page.html", context=date)
    if request.method == 'POST' and 'unsubscribe' in request.POST:
        vol_id = request.session['vol_id']
        context = {'id': vol_id}
        return render(request, "scheduling_application/unsubscribe.html", context=context)
    elif request.method == 'POST':
        vol_id = request.session['vol_id']
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
        return render(request, "scheduling_application/survey_complete.html", {})

def view_availability(request, pk):
    volunteer = Volunteer.objects.get(id=pk)
    print(volunteer)
    try:
        day1 = volunteer.Days.get(day_of_month=1)
        print(day1)
    except Day.DoesNotExist:
        for i in range(1, 32):
            Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                               day_of_month=i, volunteer=volunteer)
        day1 = volunteer.Days.get(day_of_month=1)
    day1 = volunteer.Days.get(day_of_month=1)
    day2 = volunteer.Days.get(day_of_month=2)
    day3 = volunteer.Days.get(day_of_month=3)
    day4 = volunteer.Days.get(day_of_month=4)
    day5 = volunteer.Days.get(day_of_month=5)
    day6 = volunteer.Days.get(day_of_month=6)
    day7 = volunteer.Days.get(day_of_month=7)
    day8 = volunteer.Days.get(day_of_month=8)
    day9 = volunteer.Days.get(day_of_month=9)
    day10 = volunteer.Days.get(day_of_month=10)
    day11 = volunteer.Days.get(day_of_month=11)
    day12 = volunteer.Days.get(day_of_month=12)
    day13 = volunteer.Days.get(day_of_month=13)
    day14 = volunteer.Days.get(day_of_month=14)
    day15 = volunteer.Days.get(day_of_month=15)
    day16 = volunteer.Days.get(day_of_month=16)
    day17 = volunteer.Days.get(day_of_month=17)
    day18 = volunteer.Days.get(day_of_month=18)
    day19 = volunteer.Days.get(day_of_month=19)
    day20 = volunteer.Days.get(day_of_month=20)
    day21 = volunteer.Days.get(day_of_month=21)
    day22 = volunteer.Days.get(day_of_month=22)
    day23 = volunteer.Days.get(day_of_month=23)
    day24 = volunteer.Days.get(day_of_month=24)
    day25 = volunteer.Days.get(day_of_month=25)
    day26 = volunteer.Days.get(day_of_month=26)
    day27 = volunteer.Days.get(day_of_month=27)
    day28 = volunteer.Days.get(day_of_month=28)
    day29 = volunteer.Days.get(day_of_month=29)
    day30 = volunteer.Days.get(day_of_month=30)
    day31 = volunteer.Days.get(day_of_month=31)

    data1 = {'_9_10': day1._9_10, '_10_11': day1._10_11, '_11_12': day1._11_12, '_12_1': day1._12_1, '_1_2': day1._1_2,
             'all': day1.all}
    data2 = {'_9_10': day2._9_10, '_10_11': day2._10_11, '_11_12': day2._11_12, '_12_1': day2._12_1, '_1_2': day2._1_2,
             'all': day2.all}
    data3 = {'_9_10': day3._9_10, '_10_11': day3._10_11, '_11_12': day3._11_12, '_12_1': day3._12_1, '_1_2': day3._1_2,
             'all': day3.all}
    data4 = {'_9_10': day4._9_10, '_10_11': day4._10_11, '_11_12': day4._11_12, '_12_1': day4._12_1, '_1_2': day4._1_2,
             'all': day4.all}
    data5 = {'_9_10': day5._9_10, '_10_11': day5._10_11, '_11_12': day5._11_12, '_12_1': day5._12_1, '_1_2': day5._1_2,
             'all': day5.all}
    data6 = {'_9_10': day6._9_10, '_10_11': day6._10_11, '_11_12': day6._11_12, '_12_1': day6._12_1, '_1_2': day6._1_2,
             'all': day6.all}
    data7 = {'_9_10': day7._9_10, '_10_11': day7._10_11, '_11_12': day7._11_12, '_12_1': day7._12_1, '_1_2': day7._1_2,
             'all': day7.all}
    data8 = {'_9_10': day8._9_10, '_10_11': day8._10_11, '_11_12': day8._11_12, '_12_1': day8._12_1, '_1_2': day8._1_2,
             'all': day8.all}
    data9 = {'_9_10': day9._9_10, '_10_11': day9._10_11, '_11_12': day9._11_12, '_12_1': day9._12_1, '_1_2': day9._1_2,
             'all': day9.all}
    data10 = {'_9_10': day10._9_10, '_10_11': day10._10_11, '_11_12': day10._11_12, '_12_1': day10._12_1, '_1_2': day10._1_2,
             'all': day10.all}
    data11 = {'_9_10': day11._9_10, '_10_11': day11._10_11, '_11_12': day11._11_12, '_12_1': day11._12_1, '_1_2': day11._1_2,
             'all': day11.all}
    data12 = {'_9_10': day12._9_10, '_10_11': day12._10_11, '_11_12': day12._11_12, '_12_1': day12._12_1, '_1_2': day12._1_2,
             'all': day12.all}
    data13 = {'_9_10': day13._9_10, '_10_11': day13._10_11, '_11_12': day13._11_12, '_12_1': day13._12_1, '_1_2': day13._1_2,
             'all': day13.all}
    data14 = {'_9_10': day14._9_10, '_10_11': day14._10_11, '_11_12': day14._11_12, '_12_1': day14._12_1, '_1_2': day14._1_2,
             'all': day1.all}
    data15 = {'_9_10': day15._9_10, '_10_11': day15._10_11, '_11_12': day15._11_12, '_12_1': day15._12_1, '_1_2': day15._1_2,
             'all': day15.all}
    data16 = {'_9_10': day16._9_10, '_10_11': day16._10_11, '_11_12': day16._11_12, '_12_1': day16._12_1, '_1_2': day16._1_2,
             'all': day16.all}
    data17 = {'_9_10': day17._9_10, '_10_11': day17._10_11, '_11_12': day17._11_12, '_12_1': day17._12_1, '_1_2': day17._1_2,
             'all': day17.all}
    data18 = {'_9_10': day18._9_10, '_10_11': day18._10_11, '_11_12': day18._11_12, '_12_1': day18._12_1, '_1_2': day18._1_2,
             'all': day18.all}
    data19 = {'_9_10': day19._9_10, '_10_11': day19._10_11, '_11_12': day19._11_12, '_12_1': day19._12_1, '_1_2': day19._1_2,
             'all': day19.all}
    data20 = {'_9_10': day20._9_10, '_10_11': day20._10_11, '_11_12': day20._11_12, '_12_1': day20._12_1, '_1_2': day20._1_2,
             'all': day20.all}
    data21 = {'_9_10': day21._9_10, '_10_11': day21._10_11, '_11_12': day21._11_12, '_12_1': day21._12_1, '_1_2': day21._1_2,
             'all': day21.all}
    data22 = {'_9_10': day22._9_10, '_10_11': day22._10_11, '_11_12': day22._11_12, '_12_1': day22._12_1, '_1_2': day22._1_2,
             'all': day22.all}
    data23 = {'_9_10': day23._9_10, '_10_11': day23._10_11, '_11_12': day23._11_12, '_12_1': day23._12_1, '_1_2': day23._1_2,
             'all': day23.all}
    data24 = {'_9_10': day24._9_10, '_10_11': day24._10_11, '_11_12': day24._11_12, '_12_1': day24._12_1, '_1_2': day24._1_2,
             'all': day24.all}
    data25 = {'_9_10': day25._9_10, '_10_11': day25._10_11, '_11_12': day25._11_12, '_12_1': day25._12_1, '_1_2': day25._1_2,
             'all': day25.all}
    data26 = {'_9_10': day26._9_10, '_10_11': day26._10_11, '_11_12': day26._11_12, '_12_1': day26._12_1, '_1_2': day26._1_2,
             'all': day26.all}
    data27 = {'_9_10': day27._9_10, '_10_11': day27._10_11, '_11_12': day27._11_12, '_12_1': day27._12_1, '_1_2': day27._1_2,
             'all': day27.all}
    data28 = {'_9_10': day28._9_10, '_10_11': day28._10_11, '_11_12': day28._11_12, '_12_1': day28._12_1, '_1_2': day28._1_2,
             'all': day28.all}
    data29 = {'_9_10': day29._9_10, '_10_11': day29._10_11, '_11_12': day29._11_12, '_12_1': day29._12_1, '_1_2': day29._1_2,
             'all': day29.all}
    data30 = {'_9_10': day30._9_10, '_10_11': day30._10_11, '_11_12': day30._11_12, '_12_1': day30._12_1, '_1_2': day30._1_2,
             'all': day30.all}
    data31 = {'_9_10': day31._9_10, '_10_11': day31._10_11, '_11_12': day31._11_12, '_12_1': day31._12_1, '_1_2': day31._1_2,
             'all': day31.all}

    current_month = datetime.now().strftime('%m')
    DayFormSet = modelformset_factory(Day, DayForm, fields=('_9_10', '_10_11', '_11_12', '_12_1', '_1_2', 'all'), extra=31, max_num=31)
    # DayFormSet = modelformset_factory(Day, DayForm, exclude=('volunteer', 'day_of_month'), extra=30, max_num=31)
    # data = {'form-TOTAL_FORMS': '31', 'form-INITIAL_FORMS': '0', 'form-MAX_NUM_FORMS': ''}
    formset = DayFormSet(initial=[data1, data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12,
                                  data13, data14, data15, data16, data17, data18, data19, data20, data21, data22, data23,
                                  data24, data25, data26, data27, data28, data29, data30, data31], queryset=Day.objects.none())


    if request.method == "POST":
        formset = DayFormSet(request.POST)
        if formset.is_valid():
            formset.save()
        else:
            print(formset.errors)
        return redirect('volunteer_page', pk)

    context = {
        'volunteer': volunteer,
        'formset': formset,
        'current_month': current_month,
    }
    return render(request, "scheduling_application/view_availability.html", context)

def logout(request):
    """View for logging out"""
    auth.logout(request)
    return redirect('home')

def view_appointments(request):
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments,
    }
    return render(request, 'scheduling_application/view_appointments.html', context)

def appointment_page(request, pk):
    """View for appointment profile page"""
    appointment = Appointment.objects.get(id=pk)
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get("remove_appointment"):
            appointment.delete()
            return redirect('view_appointments')
        elif request.POST.get("edit_appointment"):
            return redirect('edit_appointment', pk)
    context = {
        'appointment': appointment,
    }
    return render(request, 'scheduling_application/appointment_page.html', context)

def edit_appointment(request, pk):
    """View for editing appointment"""
    appointment = Appointment.objects.get(id=pk)
    data = {'senior': appointment.senior, 'volunteer': appointment.volunteer, 'start_address': appointment.start_address, 'end_address': appointment.end_address, 'date_and_time': appointment.date_and_time,
            'purpose_of_trip': appointment.purpose_of_trip, 'notes': appointment.notes}
    form = AppointmentForm(initial=data)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
        return redirect('appointment_page', pk)
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/edit_appointment.html', context)

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


