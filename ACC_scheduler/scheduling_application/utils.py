from .models import Volunteer, SurveyStatus
from .methods import check_time,  get_timeframes
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings
from twilio.rest import Client
from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site


def sync_galaxy(voldata, check_list):
    for i in voldata['data']:
        galaxy_id = int(i['id'])
        if galaxy_id in check_list:
            volunteer = Volunteer.objects.filter(galaxy_id=galaxy_id)
            try:
                volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                 phone=i['phone'], email=i['email'], dob=i['birthdate'], address=i['address'],
                                 additional_notes=i['extras']['availability-context'])
                if 'Email' in i['extras']['preferred-contact-method']:
                    volunteer.update(notify_email=True)
                if 'Text Message' in i['extras']['preferred-contact-method']:
                    volunteer.update(notify_text=True)
                if 'Phone Call' in i['extras']['preferred-contact-method']:
                    volunteer.update(notify_call=True)
            except KeyError:
                volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                 phone=i['phone'], email=i['email'], dob=i['birthdate'], address=i['address'])
                print("except updating", volunteer)
        else:
            # create
            try:
                Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                         phone=i['phone'], email=i['email'], dob=i['birthdate'],
                                         additional_notes=i['extras']['availability-context'])
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


def find_matches(check_list, day_of_month, day_time):
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
    return potential_list


def send_emails(potential_list, selected_volunteers, senior, appointment, domain):
    callers = []
    flag = False
    for i in potential_list:
        if str(i['id']) in selected_volunteers.getlist('volunteer'):
            flag = True
            if i['notify_email']:
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i[
                    'email'] + "&token=" + token
                email_subject = 'Volunteer Appointment Confirmation'
                email_message = f'Hello Volunteer!\n\nWe have a Senior Escort Program Participant who requests ' \
                                f'a buddy! Based on your availability, you would be a perfect match!\n' + \
                                f'\tWho: {senior[0]["first_name"]} {senior[0]["last_name"]}\n' \
                                f'\tWhat: {appointment[0]["purpose_of_trip"]}\n' \
                                f'\tWhen: {appointment[0]["date_and_time"]}\n' \
                                f'\tWhere: {appointment[0]["start_address"]} to {appointment[0]["end_address"]}\n' + \
                                'Please click the link below to accept this request.\n' + activate_url + \
                                '\n\nIf you have any questions or concerns, please call (916) 476-3192.' \
                                '\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff'
                from_email = 'acc.scheduler.care@gmail.com'
                to_email = [i['email']]
                send_mail(email_subject, email_message, from_email, to_email)
            if i['notify_text']:
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i[
                    'email'] + "&token=" + token  # MAYBE CAN REMOVE EMAIL QUERY
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH
                client = Client(account_sid, auth_token)
                message = client.messages.create(
                    body=f'Hello Volunteer!\n\nWe have a Senior Escort Program Participant who requests '
                         f'a buddy! Based on your availability, you would be a perfect match!\n' + \
                         f'\tWho: {senior[0]["first_name"]} {senior[0]["last_name"]}\n' \
                         f'\tWhat: {appointment[0]["purpose_of_trip"]}\n' \
                         f'\tWhen: {appointment[0]["date_and_time"]}\n' \
                         f'\tWhere: {appointment[0]["start_address"]} to {appointment[0]["end_address"]}\n' + \
                         'Please click the link below to accept this request.\n' + activate_url + \
                         '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,'
                         '\nSacramento Senior Saftey Collaborative Staff',
                    from_='+19569486977', to=i['phone'])
            if i['notify_call']:
                first = i['first_name']
                last = i['last_name']
                phone = i['phone']
                callers.append(f'{first} {last} {phone} ')
    return callers, flag


def notify_senior(appointment, volunteer):
    senior = appointment.senior
    if senior.notify_email:
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
    if senior.notify_text:
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


def send_monthly_surveys(request):
    sent_status = False
    dt = datetime.today()
    curr_month = dt.month
    if SurveyStatus.objects.count() == 0:
        survey = SurveyStatus.objects.create(month=curr_month, sent=False, survey_id=1)
    else:
        survey = SurveyStatus.objects.get(survey_id=1)
    if survey.sent is False or survey.month is not curr_month:
        sent_status = True
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
    return sent_status, curr_month
