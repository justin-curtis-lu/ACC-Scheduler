# Django imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.core.mail import send_mail, BadHeaderError
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.db.models.query_utils import Q
from django.utils.datastructures import MultiValueDictKeyError
# App imports
from .utils import sync_galaxy, find_matches, update_minors, notify_senior, send_monthly_surveys,\
    send_emails, read_survey_data, generate_v_days
from .forms import UserRegisterForm, SeniorForm, VolunteerForm, AppointmentForm, AuthenticationForm
from .models import Senior, Volunteer, Appointment, Day, SurveyStatus
# External imports
import requests
from datetime import datetime
import calendar
from calendar import monthrange


# Collection of views for boiler views / authentication_general
def home(response):
    """View for the general home page"""
    return render(response, "scheduling_application/authentication_general/home.html", {})


def console(request):
    """View for console page (home page when logged in).
    Allows middle man access to all user side functions"""
    if not request.user.is_authenticated:
        return render(request, 'scheduling_application/authentication_general/home.html', {})
    if len(SurveyStatus.objects.all()) == 0:
        context = {
            'vol_count': Volunteer.objects.count(),
            'sen_count': Senior.objects.count(),
        }
    else:
        month_integer = SurveyStatus.objects.last().month
        datetime_object = datetime.strptime(str(month_integer), "%m")
        full_month_name = datetime_object.strftime("%B")
        context = {
            'vol_count': Volunteer.objects.count(),
            'sen_count': Senior.objects.count(),
            'month': full_month_name
        }
    return render(request, 'scheduling_application/authentication_general/console.html', context)




def login(request):
    """View for the login page
    (uses Django's built-in AuthenticationForm)"""
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            # Syncing with Galaxy
            url = 'https://api2.galaxydigital.com/volunteer/user/list/'
            headers = {'Accept': 'scheduling_application/json'}
            params = {'key': settings.GALAXY_AUTH, 'return[]': "extras"}  # will need to include tags
            response = requests.get(url, headers=headers, params=params)
            vol_data = response.json()
            check_list = Volunteer.objects.values_list('galaxy_id', flat=True)
            try:
                # sync_galaxy(vol_data, check_list)
                print("synced galaxy")
            except KeyError:    # FOR IF THE GALAXY API KEY IS INCORRECT
                messages.warning(request, f'Unsuccessful attempt at updating Galaxy Digital Data!')
            return redirect('console')
        else:
            messages.error(request, 'invalid credentials')
            return redirect('login')
    context = {
        'form': form,
    }
    return render(request, 'scheduling_application/authentication_general/login.html', context)


def logout(request):
    """View for logging out"""
    auth.logout(request)
    return redirect('home')


def register(request):
    """View for the registration page
    (uses Django's built-in UserRegisterForm)"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'scheduling_application/authentication_general/register.html', context)


def keys(request):
    """View which reads for a valid link that allows
    creation of a middle man account (keys stored in .env)"""
    if request.method == 'GET':
        if request.GET.get('token') == settings.KEY1:
            return redirect('register')
        else:
            return render(request, 'scheduling_application/bad_link.html')


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "scheduling_application/password_reset/password_reset_email"
                    from_email = 'acc.scheduler.care@gmail.com'
                    c = {
                        "email": user.email,
                        'domain': '127.0.0.1:8000',         # CHANGE FOR DEPLOYMENT
                        'site_name': 'ACC Scheduler',       # CHANGE FOR DEPLOYMENT
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, from_email, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="scheduling_application/password_reset/password_reset.html", context={"password_reset_form":password_reset_form})


# Collection of views for View Appointments, View Participants, View Volunteers
def view_appointments(request):
    appointments = Appointment.objects.all()
    context = {
        'appointments': appointments,
    }
    return render(request, 'scheduling_application/appointments/view_appointments.html', context)


def appointment_page(request, pk):
    """View for appointment profile page"""
    appointment = Appointment.objects.get(id=pk)
    if request.method == 'POST':
        if request.POST.get("remove_appointment"):
            appointment.delete()
            return redirect('view_appointments')
        elif request.POST.get("edit_appointment"):
            return redirect('edit_appointment', pk)
    context = {
        'appointment': appointment,
    }
    return render(request, 'scheduling_application/appointments/appointment_page.html', context)


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
    return render(request, 'scheduling_application/appointments/edit_appointment.html', context)


def view_seniors(request):
    """View for the seniors page (table of all the seniors in the database)"""
    seniors = Senior.objects.all()
    context = {
        'seniors': seniors,
    }
    return render(request, 'scheduling_application/seniors/view_seniors.html', context)


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
    return render(request, 'scheduling_application/seniors/add_senior.html', context)


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
    return render(request, 'scheduling_application/seniors/edit_senior.html', context)


def senior_page(request, pk):
    """View for senior profile page"""
    senior = Senior.objects.get(id=pk)
    if request.method == 'POST':
        if request.POST.get("remove_senior"):
            senior.delete()
            return redirect('view_seniors')
        elif request.POST.get("edit_senior"):
            return redirect('edit_senior', pk)
    context = {
        'senior': senior,
    }
    return render(request, 'scheduling_application/seniors/senior_page.html', context)


def view_volunteers(request):
    """View for the volunteers page (table of all the volunteers in the database)"""
    volunteers = Volunteer.objects.all()
    context = {
        'volunteers': volunteers,
    }
    return render(request, 'scheduling_application/volunteers/view_volunteers.html', context)


def add_volunteer(request):
    """View for adding volunteer page"""
    form = VolunteerForm()
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        try:
            if request.POST['notify_email'] == "on" or request.POST['notify_text'] == "on" or request.POST[
                'notify_call'] == "on":
                if form.is_valid():
                    form.save()
                    return redirect('view_volunteers')
                else:
                    messages.error(request, "Invalid Form.")
                    return redirect('add_volunteer')
        except:
            messages.error(request, "Please select one notification method")
            return redirect('add_volunteer')
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/volunteers/add_volunteer.html', context)


def edit_volunteer(request, pk):
    """View for editing volunteer"""
    volunteer = Volunteer.objects.get(id=pk)
    data = {'galaxy_id': volunteer.galaxy_id, 'last_name': volunteer.last_name, 'first_name': volunteer.first_name, 'phone': volunteer.phone, 'email': volunteer.email, 'dob': volunteer.dob,
            'vaccinated': volunteer.vaccinated,'notify_email': volunteer.notify_email, 'notify_text': volunteer.notify_text, 'notify_call': volunteer.notify_call,
            'current_appointments': volunteer.Appointments.all(), 'additional_notes': volunteer.additional_notes, 'unsubscribed': volunteer.unsubscribed}
    form = VolunteerForm(initial=data)
    if request.method == 'POST':
        form = VolunteerForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
        return redirect('volunteer_page', pk)
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/volunteers/edit_volunteer.html', context)


def view_availability(request, pk, month, year):
    DayFormSet, volunteer, formset, month = generate_v_days(pk, int(month), int(year))
    if request.method == 'POST' and 'datepicker' not in request.POST:
        formset = DayFormSet(request.POST)
        if formset.is_valid():
            formset.save()
        else:
            print(formset.errors)
        return redirect('volunteer_page', pk)
    elif request.method == 'POST' and 'datepicker' in request.POST:
        date = request.POST.get('datepicker').split('/')
        month = date[0]
        year = date[1]
        return redirect('view_availability', pk, month, year)
    context = {
        'volunteer': volunteer,
        'formset': formset,
        'month': month,
    }
    return render(request, "scheduling_application/volunteers/view_availability.html", context)

def volunteer_page(request, pk):
    """View for volunteer profile page"""
    volunteer = Volunteer.objects.get(id=pk)
    dt = datetime.today()
    curr_month = str(dt.month)
    curr_year = str(dt.year)
    if request.method == 'POST':
        if request.POST.get("remove_volunteer"):
            volunteer.delete()
            return redirect('view_volunteers')
        elif request.POST.get("edit_volunteer"):
            return redirect('edit_volunteer', pk)
    context = {
        'volunteer': volunteer,
        'current_month': curr_month,
        'current_year': curr_year
    }
    return render(request, 'scheduling_application/volunteers/volunteer_page.html', context)


# Collection of views for Sync GalaxyDigital, SendSurveys, and Schedule an Appointment
def galaxy_update_volunteers(request):
    """View which pulls volunteer data from Galaxy Digital
    API and updates on app side"""
    if request.GET.get("sync_GalaxyDigital"):
        url = 'https://api2.galaxydigital.com/volunteer/user/list/'
        headers = {'Accept': 'scheduling_application/json'}
        params = {'key': settings.GALAXY_AUTH, 'return[]': "extras"}
        response = requests.get(url, headers=headers, params=params)
        vol_data = response.json()
        check_list = Volunteer.objects.values_list('galaxy_id', flat=True)
        try:
            sync_galaxy(vol_data, check_list)
            messages.success(request, f'Successfully updated the application with Galaxy Digital Data!')
        except:
            messages.warning(request, f'Unsuccessful attempt at updating Galaxy Digital Data!')
    return redirect('console')

def make_appointment(request):
    """View for the page where users can schedule an appointment.
       Shows current seniors, volunteers, and appointments.
       Allows users to choose a senior and day then continue."""
    seniors_list = Senior.objects.all()
    volunteers_list = Volunteer.objects.all()
    if request.method == 'POST':
        senior_id = request.POST['senior_id']
        date = request.POST['date']
        start_time = request.POST['start_time'].split(':')
        start_time_number = int(start_time[0]) + int(start_time[1])
        end_time = request.POST['end_time'].split(':')
        end_time_number = int(end_time[0]) + int(end_time[1])
        if end_time_number <= start_time_number:
            messages.error(request, "Invalid appointment time period.")
            return redirect('make_appointment')
        time_period = request.POST['start_time'] + '-' + request.POST['end_time']
        # day_of_month = int(day_time[0].split('/')[1])
        check_list = Day.objects.filter(date=date).values_list("volunteer", flat=True)
        potential_list = find_matches(check_list, date, time_period)
        if not potential_list:
            messages.error(request, "No volunteers are available at this time.")
            return redirect('make_appointment')
        request.session['potential_list'] = list(potential_list)
        request.session['senior'] = senior_id
        request.session['date'] = date
        request.session['time_period'] = time_period
        return redirect('confirm_volunteers')
    context = {
        'seniors_list': seniors_list[:5],
        'volunteers_list': volunteers_list[:5]
    }
    return render(request, 'scheduling_application/make_appointment/make_appointment.html', context)


def confirm_volunteers(request):
    """View for page to confirm which volunteers to send emails to. (Follows make_appointment)"""
    potential_list = request.session['potential_list']
    senior = Senior.objects.get(id=request.session['senior'])
    context = {
        'potential_list': potential_list,
        'date': request.session['date'],
        'senior': senior
    }
    update_minors(potential_list)
    if request.method == 'POST':
        start_address = request.POST['start_address']
        end_address = request.POST['end_address']
        purpose_of_trip = request.POST['purpose_of_trip']
        additional_notes = request.POST['notes']
        appointment = Appointment.objects.create(senior=senior, start_address=start_address
                                                 , end_address=end_address
                                                 , date_and_time=request.session['date'] + " " + request.session['time_period']
                                                 , purpose_of_trip=purpose_of_trip, notes=additional_notes)
        selected_volunteers = request.POST
        domain = get_current_site(request).domain
        appointment = Appointment.objects.filter(id=appointment.id, volunteer=None).values()
        senior = Senior.objects.filter(id=appointment[0]['senior_id']).values()
        callers, sent_flag, invalid_emails, invalid_phone = send_emails(potential_list, selected_volunteers, senior, appointment, domain, appointment[0]['id'])
        if sent_flag:
            if callers:
                messages.success(request, f'Emails/texts sent successfully! '
                                          f'Please manually call the following volunteers {callers}')
            else:
                messages.success(request,
                                 f'Emails/texts successfully sent to volunteers!')
            if len(invalid_emails) != 0:
                messages.error(request, f'Emails have not been sent to the following volunteers as their emails are invalid {invalid_emails}')
            if len(invalid_phone) != 0:
                messages.error(request, f'Texts have not been sent to the following volunteers as their phone numbers are invalid {invalid_phone}')
            return redirect('confirm_volunteers')
    return render(request, 'scheduling_application/make_appointment/confirm_v.html', context)


def success(request):
    """View for the email sending success page
    (This is when a volunteer clicks a confirmation link)"""
    if request.method == 'GET':
        vol_id = request.GET.get('id')
        app_id = int(request.GET.get('appointment_id'))
        try:
            volunteer = Volunteer.objects.get(id=vol_id)
            empty_appointment = Appointment.objects.filter(id=app_id, volunteer=None)
            if not empty_appointment:
                return redirect('vol_already_selected')
            empty_appointment.update(volunteer=volunteer)
            appointment = Appointment.objects.get(id=app_id)
            notify_senior(appointment, volunteer)
        except (KeyError, Appointment.DoesNotExist):
            appointment = None
        context = {
            'appointment': appointment
        }
        return render(request, "scheduling_application/make_appointment/success.html", context)


def vol_already_selected(request):
    """View for the email when a volunteer has already matched with a participant
    (This is when a volunteer clicks a confirmation link)"""
    return render(request, "scheduling_application/make_appointment/vol_already_selected.html", {})


def send_survey(request):
    """View for middle man to send the monthly surveys"""
    if request.GET.get('send_survey'):
        date = request.GET['datepicker'].split('/')
        month = date[0]
        year = date[1]
        sent_status, invalid_emails, invalid_phone = send_monthly_surveys(request, month, year)
        if sent_status:
            messages.success(request, f'Successfully sent surveys for the month of {calendar.month_name[int(month)]}.')
            if len(invalid_emails) != 0:
                messages.error(request, f'Emails have not been sent to the following volunteers as their emails are invalid {invalid_emails}')
            if len(invalid_phone) != 0:
                messages.error(request, f'Texts have not been sent to the following volunteers as their phone numbers are invalid {invalid_phone}')
        else:
            messages.error(request, f'You have already sent surveys for the month of {calendar.month_name[int(month)]}.')
    return redirect('pre_send_survey')


def pre_send_survey(request):
    """Extra view which helps prevent mis-clicks of monthly survey sending"""
    return render(request, 'scheduling_application/survey_sending/survey_confirmation.html')


def survey_page(request):
    """View extracts the data that a volunteer fills out from the monthly survey
    and updates the data on app side accordingly"""
    if request.method == 'GET':
        request.session['vol_id'] = request.GET.get('id')
        request.session['vol_email'] = request.GET.get('email')
        request.session['vol_token'] = request.GET.get('token')
        request.session['survey_month'] = request.GET.get('month')
        request.session['survey_year'] = request.GET.get('year')
        days = monthrange(int(request.session['survey_year']), int(request.session['survey_month']))[1]
        vol_id = request.session['vol_id']
        vol_token = request.session['vol_token']
        volunteer = Volunteer.objects.get(id=vol_id)
        month = request.session['survey_month']
        context = {
            'month': month,
            'num_days': range(days)
        }
        # Validate the token inside of the URL
        if vol_token != volunteer.survey_token:
            return render(request, "scheduling_application/bad_link.html", {})
        else:
            return render(request, "scheduling_application/survey_sending/survey_page.html", context=context)
    if request.method == 'POST' and 'unsubscribe' in request.POST:
        vol_id = request.session['vol_id']
        return render(request, "scheduling_application/unsubscribe.html", context={})
    elif request.method == 'POST' and 'confirm_unsubscribe' in request.POST:
        comms = request.POST.get('comms')
        everything = request.POST.get('everything')
        vol_id = request.session['vol_id']
        # Unsubscribe SMS/Email
        if comms:
            volunteer = Volunteer.objects.get(id=vol_id)
            volunteer.notify_email = False
            volunteer.notify_text = False
            volunteer.save()
        # Unsubscribe from entire service
        if everything:
            volunteer = Volunteer.objects.get(id=vol_id)
            volunteer.notify_email = False
            volunteer.notify_text = False
            volunteer = Volunteer.objects.get(id=vol_id)
            volunteer.Days.filter(volunteer=volunteer).delete()
            volunteer.unsubscribed = True
            volunteer.save()
        return render(request, "scheduling_application/survey_sending/survey_complete.html", {})
    elif request.method == 'POST':
        vol_id = request.session['vol_id']
        option_list = request.POST.getlist('survey-value')
        volunteer = Volunteer.objects.get(id=vol_id)
        if int(request.session['survey_month']) < 10:
            month_string = "0" + request.session['survey_month']
        else:
            month_string = request.session['survey_month']
        regex = r'((' + month_string + r')[/]\d\d[/](' + request.session['survey_year'] + r'))'
        print(volunteer.Days.all().filter(date__regex=regex))
        volunteer.Days.all().filter(date__regex=regex).delete()
        read_survey_data(option_list, volunteer, request.session['survey_month'], request.session['survey_year'])
        return render(request, "scheduling_application/survey_sending/survey_complete.html", {})
