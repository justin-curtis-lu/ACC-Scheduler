# Django imports
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
# App imports
from .utils import sync_galaxy, find_matches, update_minors, notify_senior, send_monthly_surveys,\
    send_emails, read_survey_data, generate_v_days
from .forms import UserRegisterForm, SeniorForm, VolunteerForm, AppointmentForm, LoginForm, KeyForm
from .models import Senior, Volunteer, Appointment, Day
# External imports
import requests
from datetime import datetime


# Collection of views for boiler views / authentication_general
def home(response):
    """View for the general home page"""
    return render(response, "scheduling_application/authentication_general/home.html", {})


def console(request):
    """View for console page (home page when logged in).
    Allows middle man access to all user side functions"""
    if not request.user.is_authenticated:
        return render(request, 'scheduling_application/authentication_general/home.html', {})
    return render(request, 'scheduling_application/authentication_general/console.html', {})


def login(request):
    """View for the login page"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                # If user exists in database
                auth.login(request, user)
                return redirect('console')
            else:
                # Else user does not exist in database
                messages.info(request, 'invalid credentials')
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'scheduling_application/authentication_general/login.html', {'form': form})


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
    return render(request, 'scheduling_application/authentication_general/register.html', {'form': form})


def keys(request):
    """View which requires valid keys in order
    to create a middle man account (keys stored in .env)"""
    if request.method == 'POST':
        form = KeyForm(request.POST)
        if form.is_valid():
            key1 = form.cleaned_data['key1']
            key2 = form.cleaned_data['key2']
            key3 = form.cleaned_data['key3']
            if key1 == settings.KEY1 and key2 == settings.KEY2 and key3 == settings.KEY3:
                return redirect('register')
            else:
                messages.info(request, 'invalid credentials')
                return redirect('keys')
    else:
        form = KeyForm()
    return render(request, 'scheduling_application/authentication_general/keys.html', {'form': form})


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
        if form.is_valid():
            form.save()
        return redirect('view_volunteers')
    context = {
        'form': form
    }
    return render(request, 'scheduling_application/volunteers/add_volunteer.html', context)


def edit_volunteer(request, pk):
    """View for editing volunteer"""
    volunteer = Volunteer.objects.get(id=pk)
    data = {'galaxy_id': volunteer.galaxy_id, 'last_name': volunteer.last_name, 'first_name': volunteer.first_name, 'phone': volunteer.phone, 'email': volunteer.email, 'dob': volunteer.dob,
            'vaccinated': volunteer.vaccinated,'notify_email': volunteer.notify_email, 'notify_text': volunteer.notify_text, 'notify_call': volunteer.notify_call,
            'current_appointments': volunteer.current_appointments, 'additional_notes': volunteer.additional_notes, 'unsubscribed': volunteer.unsubscribed}
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


def view_availability(request, pk):
    DayFormSet, volunteer, formset, current_month = generate_v_days(pk)
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
    return render(request, "scheduling_application/volunteers/view_availability.html", context)


def volunteer_page(request, pk):
    """View for volunteer profile page"""
    volunteer = Volunteer.objects.get(id=pk)
    if request.method == 'POST':
        if request.POST.get("remove_volunteer"):
            volunteer.delete()
            return redirect('view_volunteers')
        elif request.POST.get("edit_volunteer"):
            return redirect('edit_volunteer', pk)
    context = {
        'volunteer': volunteer,
    }
    return render(request, 'scheduling_application/volunteers/volunteer_page.html', context)


# Collection of views for Sync GalaxyDigital, SendSurveys, and Schedule an Appointment
def galaxy_update_volunteers(request):
    """View which pulls volunteer data from Galaxy Digital
    API and updates on app side"""
    if request.GET.get("galaxy_update_volunteers"):
        url = 'https://api2.galaxydigital.com/volunteer/user/list/'
        headers = {'Accept': 'scheduling_application/json'}
        params = {'key': settings.GALAXY_AUTH, 'return[]': "extras"}
        response = requests.get(url, headers=headers, params=params)
        vol_data = response.json()
        check_list = Volunteer.objects.values_list('galaxy_id', flat=True)
        sync_galaxy(vol_data, check_list)
    return redirect('console')


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
    if request.method == 'POST':
        senior = request.POST['senior']
        start_address = request.POST['start_address']
        end_address = request.POST['end_address']
        purpose_of_trip = request.POST['purpose_of_trip']
        additional_notes = request.POST['notes']
        day_time = request.POST['day_time'].split()
        senior_id = Senior.objects.get(id=senior)
        day_of_month = int(day_time[0].split('/')[1])
        check_list = Day.objects.filter(day_of_month=day_of_month).values_list("volunteer", flat=True)
        potential_list = find_matches(check_list, day_of_month, day_time)
        if not potential_list:
            messages.error(request, "No volunteers are available at this time.")
            return redirect('make_appointment')
        # appointment = Appointment.objects.create(senior=senior_id, start_address=start_address
        #                                          , end_address=end_address
        #                                          , date_and_time=day_time[0] + " " + day_time[1]
        #                                          , purpose_of_trip=purpose_of_trip, notes=additional_notes)
        # request.session['appointment'] = appointment.id
        # request.session['potential_list'] = list(potential_list)
        request.session['senior'] = senior
        request.session['start_address'] = start_address
        request.session['end_address'] = end_address
        request.session['purpose_of_trip'] = purpose_of_trip
        request.session['additional_notes'] = additional_notes
        request.session['day_time'] = day_time
        return redirect('confirm_volunteers')
    return render(request, 'scheduling_application/make_appointment/make_appointment.html', context)


def confirm_volunteers(request):
    """View for page to confirm which volunteers to send emails to. (Follows make_appointment)"""
    potential_list = request.session['potential_list']
    senior_id = Senior.objects.get(id=request.session['senior'])
    context = {
        'potential_list': potential_list
    }
    update_minors(potential_list)
    if request.method == 'POST':
        appointment = Appointment.objects.create(senior=senior_id, start_address=request.session['start_address']
                                                 , end_address=request.session['end_address']
                                                 , date_and_time=request.session['day_time'][0] + " " + request.session['day_time'][1]
                                                 , purpose_of_trip=request.session['purpose_of_trip'], notes=request.session['additional_notes'])
        selected_volunteers = request.POST
        domain = get_current_site(request).domain
        appointment = Appointment.objects.filter(id=appointment.id, volunteer=None).values()
        senior = Senior.objects.filter(id=appointment[0]['senior_id']).values()
        callers, sent_flag = send_emails(potential_list, selected_volunteers, senior, appointment, domain)
        if sent_flag:
            if callers:
                messages.success(request, f'Emails/texts sent successfully! '
                                          f'Please manually call the following volunteers{callers}')
            else:
                messages.success(request,
                                 f'Emails/texts sent successfully!')
            return redirect('confirm_volunteers')
    return render(request, 'scheduling_application/make_appointment/confirm_v.html', context)


def success(request):
    """View for the email sending success page
    (This is when a volunteer clicks a confirmation link)"""
    if request.method == 'GET':
        vol_id = request.GET.get('id')
        try:
            volunteer = Volunteer.objects.get(id=vol_id)
            empty_appointment = Appointment.objects.filter(id=request.session['appointment'], volunteer=None)
            if not empty_appointment:
                return redirect('vol_already_selected')
            empty_appointment.update(volunteer=volunteer)
            appointment = Appointment.objects.get(id=request.session['appointment'])
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
        sent_status, curr_month = send_monthly_surveys(request)
        if sent_status:
            messages.success(request, f'Successfully sent surveys for the month of {curr_month}.')
        else:
            messages.warning(request, f'You have already sent surveys for the month of {curr_month}.')
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
        vol_id = request.session['vol_id']
        vol_token = request.session['vol_token']
        volunteer = Volunteer.objects.get(id=vol_id)
        current_month = datetime.now().strftime('%m')
        date = {'month': current_month}
        # Validate the token inside of the URL
        if vol_token != volunteer.survey_token:
            return render(request, "scheduling_application/bad_link.html", {})
        else:
            return render(request, "scheduling_application/survey_sending/survey_page.html", context=date)
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
        volunteer.Days.filter(volunteer=volunteer).delete()
        read_survey_data(option_list, volunteer)
        return render(request, "scheduling_application/survey_sending/survey_complete.html", {})
