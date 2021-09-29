# Django imports
from django.utils.crypto import get_random_string
from django.contrib.sites.shortcuts import get_current_site
from django.forms import modelformset_factory
from django.core.mail import send_mail
from django.conf import settings
# External imports
from twilio.rest import Client, TwilioRestClient, TwilioException
from datetime import datetime
from smtplib import SMTPRecipientsRefused
import calendar
from calendar import monthrange
import re
# App imports
from .models import Volunteer, SurveyStatus, Day
from .methods import check_time,  get_timeframes, check_age, appointment_conflict
from .forms import DayForm


def sync_galaxy(vol_data, check_list):
    pattern = re.compile("(\d\d\d\d)[-](\d\d)[-](\d\d)")
    for i in vol_data['data']:
        #print(i)
        #print(i['firstName'], i['lastName'], i['tags'])
        galaxy_id = int(i['id'])
        if galaxy_id in check_list:
            volunteer = Volunteer.objects.filter(galaxy_id=galaxy_id)
            # print(volunteer)
            # Flag to skip updating if unsubscribed is true
            if not volunteer[0].unsubscribed:
                try:
                    if pattern.match(str(i['birthdate'])) is not None:
                        date = str(i['birthdate']).split('-')
                        formatted_date = date[1] + "/" + date[2] + "/" + date[0]
                    else:
                        formatted_date = "N/A"
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                     phone=i['phone'], email=i['email'], dob=formatted_date, address=i['address'],
                                     additional_notes=i['extras']['availability-context'])
                    if 'Email' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_email=True)
                    if 'Text Message' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_text=True)
                    if 'Phone Call' in i['extras']['preferred-contact-method']:
                        volunteer.update(notify_call=True)
                except KeyError:
                    if pattern.match(str(i['birthdate'])) is not None:
                        date = str(i['birthdate']).split('-')
                        formatted_date = date[1] + "/" + date[2] + "/" + date[0]
                    else:
                        formatted_date = "N/A"
                    volunteer.update(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                     phone=i['phone'], email=i['email'], dob=formatted_date, address=i['address'])
                    print("except updating", volunteer)
        else:
            # create
            #print("create")
            if 'sacssc' in i["tags"] or 'SacSSC' in i["tags"]:
                try:
                    if pattern.match(str(i['birthdate'])) is not None:
                        date = str(i['birthdate']).split('-')
                        formatted_date = date[1] + "/" + date[2] + "/" + date[0]
                    else:
                        formatted_date = "N/A"
                    #print(formatted_date)
                    Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                             phone=i['phone'], email=i['email'], dob=formatted_date, notify_call=True,
                                             additional_notes=i['extras']['availability-context'])
                    volunteer = Volunteer.objects.filter(galaxy_id=galaxy_id)
                    #print(i)
                    if 'Email' in i['extras']['preferred-contact-method']:
                        #print("email")
                        volunteer.update(notify_email=True)
                    if 'Text Message' in i['extras']['preferred-contact-method']:
                        #print("text")
                        volunteer.update(notify_text=True)
                    if 'Phone Call' in i['extras']['preferred-contact-method']:
                        #print("call")
                        volunteer.update(notify_call=True)
                    print("try creating", i['firstName'], i['lastName'])
                except KeyError:
                    if pattern.match(str(i['birthdate'])) is not None:
                        date = str(i['birthdate']).split('-')
                        formatted_date = date[1] + "/" + date[2] + "/" + date[0]
                    else:
                        formatted_date = "N/A"
                    Volunteer.objects.create(galaxy_id=galaxy_id, last_name=i['lastName'], first_name=i['firstName'],
                                             phone=i['phone'], email=i['email'], dob=formatted_date, notify_call=True)
                    print("except creating", i['firstName'], i['lastName'])


def find_matches(check_list, date, time_period):
    potential_list = []
    for volunteer in check_list:
        volunteer_object = Volunteer.objects.filter(id=volunteer)
        availability = volunteer_object[0].Days.filter(date=date)[0]
        if availability.all:
            check_conflict = volunteer_object[0].Appointments.filter(date_and_time__contains=date)
            schedule_conflict = False
            for appointment in check_conflict:
                if appointment_conflict(time_period, appointment.date_and_time.split(' ')[1]):
                    schedule_conflict = True
                    break
            if not schedule_conflict:
               potential_list.append(volunteer_object.values()[0])
        else:
            time_frames = get_timeframes([availability._9_10, availability._10_11, availability._11_12, availability._12_1, availability._1_2])
            for time in time_frames:
                if check_time(time_period, time):
                    check_conflict = volunteer_object[0].Appointments.filter(date_and_time__contains=date)
                    break_check = False
                    for appointment in check_conflict:
                        if appointment_conflict(time_period, appointment.date_and_time.split(' ')[1]):
                            break_check = True
                            break
                    if break_check:
                        break
                    volunteer_object[0].Appointments.filter()
                    potential_list.append(volunteer_object.values()[0])
                    break
    return potential_list


def update_minors(potential_list):
    pattern = re.compile("(\d\d)[/](\d\d)[/](\d\d\d\d)")
    for volunteer in potential_list:
        if pattern.match(volunteer['dob']) is not None and check_age(volunteer['dob']):
            volunteer['minor'] = True
        else:
            volunteer['minor'] = False
    for volunteer in potential_list:
        set_minor = Volunteer.objects.get(id=volunteer['id'])
        if pattern.match(set_minor.dob) is not None and check_age(set_minor.dob):
            set_minor.minor = True
            set_minor.save()
        else:
            set_minor.minor = False
            set_minor.save()


def send_emails(potential_list, selected_volunteers, senior, appointment, domain, appointment_id):
    callers = []
    flag = False
    invalid_emails = []
    invalid_phone = []
    for i in potential_list:
        print(i)
        if str(i['id']) in selected_volunteers.getlist('volunteer'):
            flag = True
            if i['notify_email']:
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i[
                    'email'] + "&token=" + token + "&appointment_id=" + str(appointment_id)
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
                from_email = settings.EMAIL_HOST_USER
                to_email = [i['email']]
                try:
                    send_mail(email_subject, email_message, from_email, to_email)
                except SMTPRecipientsRefused:
                    print(f"{to_email} is not a valid email.")
                    invalid_emails.append(i['first_name'] + " " + i['last_name'])
            if i['notify_text']:
                token = get_random_string(length=32)
                activate_url = 'http://' + domain + "/success" + "/?id=" + str(i['id']) + "&email=" + i[
                    'email'] + "&token=" + token  # MAYBE CAN REMOVE EMAIL QUERY
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH
                client = Client(account_sid, auth_token)
                try:
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
                except TwilioException:
                    print(f"{i['phone']} is not a valid phone number.")
                    invalid_phone.append(i['first_name'] + " " + i['last_name'])
            if i['notify_call']:
                first = i['first_name']
                last = i['last_name']
                phone = i['phone']
                callers.append(f'{first} {last} {phone} ')
    return callers, flag, invalid_emails, invalid_phone


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
        from_email = settings.EMAIL_HOST_USER
        to_email = [senior.email]
        try:
            send_mail(email_subject, email_message, from_email, to_email)
        except SMTPRecipientsRefused:
            print(f"{to_email} is not a valid email.")
    if senior.notify_text:
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH
        client = Client(account_sid, auth_token)
        try:
            message = client.messages.create(
                body=f'Hello Participant!\n\nWe have a Senior Escort Program Volunteer who has accepted your request! Here are the details of the appointment!\n' + \
                     f'\tVolunteer: {volunteer.first_name} {volunteer.last_name}\n' \
                     f'\tWhat: {appointment.purpose_of_trip}\n' \
                     f'\tWhen: {appointment.date_and_time}\n' \
                     f'\tWhere: {appointment.start_address} to {appointment.end_address}\n' + \
                     '\n\nIf you have any questions or concerns, please call (916) 476-3192.\n\nSincerely,\nSacramento Senior Saftey Collaborative Staff',
                from_='+19569486977', to=senior.phone)
        except TwilioException:
            print(f"{senior.phone} is not a valid phone number.")


def send_monthly_surveys(request, month, year):
    sent_status = False
    invalid_emails = []
    invalid_phone = []
    dt = datetime.today()
    date_sent = str(dt.month) + "/" + str(dt.day) + "/" + str(dt.year)
    # if SurveyStatus.objects.filter(month=month).filter(year=year).count() != 0:
    survey = SurveyStatus.objects.create(month=month, year=year, sent=False, date_sent=date_sent)

    sent_status = True
    domain = get_current_site(request).domain
    for i in Volunteer.objects.all():
        token = get_random_string(length=32)
        i.survey_token = token
        activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&month=" + month + "&year=" + year +  "&email=" + i.email \
                       + "&token=" + token
        if i.notify_email:
            email_subject = 'Volunteer Availability Survey'
            email_message = "Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the month of " + calendar.month_name[int(month)] + ". " \
                            "If you do not fill out the survey, your previous times will be carried over for the month of " + calendar.month_name[int(month)] + ". " \
                            "Your time is so appreciated and we could not provide seniors with free programs without you!" \
                            "\n" + activate_url + "\n\nSincerely,\nSenior Escort Program Staff"
            from_email = settings.EMAIL_HOST_USER
            to_email = [i.email]
            try:
                send_mail(email_subject, email_message, from_email, to_email)
            except SMTPRecipientsRefused:
                print(f"{to_email} is not a valid email.")
                invalid_emails.append(i.first_name + " " + i.last_name)
            emails_sent = True
        if i.notify_text:
            account_sid = settings.TWILIO_ACCOUNT_SID
            auth_token = settings.TWILIO_AUTH
            client = Client(account_sid, auth_token)
            try:
                message = client.messages.create(
                    body="Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the month of "
                         + calendar.month_name[month] + ". "f"If you do not fill out the survey, your previous "
                                                               f"times will be carried over for the month of " +
                         calendar.month_name[month] + ". " + f"Your time is so appreciated and we could not "
                                                                    f"provide seniors with free programs without you!"
                         + f"\n{activate_url}\n\nSincerely,\nSenior Escort Program Staff",
                    from_='+19569486977', to=i.phone)
            except TwilioException:
                print(f"{i.phone} is not a valid phone number.")
                invalid_phone.append(i.first_name + " " + i.last_name)
        # availability creation
        try:                # creates new month objects w/ last month's info if user has availability from last month
            most_recent_day = i.Days.last().date
            prev_month = most_recent_day[0:2]
            num_prev_days = int(most_recent_day[3:5])
            prev_days = i.Days.all()[:num_prev_days]
            print(len(prev_days))
            print("MONTHRANGE", monthrange(int(year), int(month))[1])
            print("prev_month", prev_month)
            print("month", month)
            if prev_month != month:
                for j in range(0, monthrange(int(year), int(month))[1]):
                    if j < 9:
                        day = "0" + str(j + 1)
                    else:
                        day = str(j + 1)
                    try:
                        Day.objects.create(_9_10=prev_days[j]._9_10, _10_11=prev_days[j]._10_11, _11_12=prev_days[j]._11_12,
                                           _12_1=prev_days[j]._12_1, _1_2=prev_days[j]._1_2, all=prev_days[j].all,
                                           date=month + '/' + day + '/' + year, volunteer=i)
                    except IndexError:
                        Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                                           date=month + '/' + day + '/' + year, volunteer=i)
        except AttributeError:      # if volunteer has no data create new day objects
            for j in range(0, monthrange(int(year), int(month))[1]):
                if j < 9:
                    day = "0" + str(j + 1)
                else:
                    day = str(j + 1)
                Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                                   date=month + '/' + day + '/' + year, volunteer=i)
            print("ATTRIBUTE ERROR")
        i.survey_token = token
        i.save()
        # survey.month = curr_month
    survey.sent = True
    survey.save()
    return sent_status, invalid_emails, invalid_phone


def read_survey_data(option_list, volunteer, month, year):
    for i in range(1, monthrange(int(year), int(month))[1] + 1):
        if int(month) < 10:
            if i < 10:
                day_string = "0" + str(i)
            else:
                day_string = str(i)
            date_string = "0" + str(month) + "/" + day_string + "/" + str(year)
        else:
            if i < 10:
                day_string = "0" + str(i)
            else:
                day_string = str(i)
            date_string = str(month) + "/" + day_string + "/" + str(year)
        Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                           date=date_string, volunteer=volunteer)
    for i in option_list:
        date = i[6:].split("-")
        if int(date[0]) < 10:
            day_string = "0" + date[0]
        else:
            day_string = date[0]
        if int(month) < 10:
            date_string = "0" + str(month) + "/" + day_string + "/" + str(year)
        else:
            date_string = str(month) + "/" + day_string + "/" + str(year)
        day = volunteer.Days.get(date=date_string)
        if date[1] == "0":
            day._9_10 = True
            day.save()
        elif date[1] == "1":
            day._10_11 = True
            day.save()
        elif date[1] == "2":
            day._11_12 = True
            day.save()
        elif date[1] == "3":
            day._12_1 = True
            day.save()
        elif date[1] == "4":
            day._1_2 = True
            day.save()
        elif date[1] == "5":
            day.all = True
            day.save()


def generate_v_days(pk, month, year):
    volunteer = Volunteer.objects.get(id=pk)
    days_in_month = monthrange(year, month)[1]
    if month < 10:
        month = '0' + str(month)
        year = str(year)
    else:
        month = str(month)
        year = str(year)
    try:
        day1 = volunteer.Days.get(date=month + '/' + '01' + '/' + year)
    except Day.DoesNotExist:
        print("CREATING DAYS")
        for i in range(1, days_in_month+1):
            if i < 10:
                day = '0' + str(i)
            else:
                day = str(i)
            Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                               date=month + '/' + day + '/' + year, volunteer=volunteer)
        day1 = volunteer.Days.get(date=month + '/' + '01' + '/' + year)
    day_dict = {}
    for i in range(1, days_in_month+1):
        if i < 10:
            day = '0' + str(i)
        else:
            day = str(i)
        day_dict[i] = volunteer.Days.get(date=month + '/' + day + '/' + year)
    data_dict = {}
    for i in range(1, days_in_month+1):
        data_dict[i] = {'_9_10': day_dict[i]._9_10, '_10_11': day_dict[i]._10_11, '_11_12': day_dict[i]._11_12, '_12_1': day_dict[i]._12_1, '_1_2': day_dict[i]._1_2, 'all': day_dict[i].all}
    # current_month = datetime.now().strftime('%m')
    DayFormSet = modelformset_factory(Day, DayForm, fields=('_9_10', '_10_11', '_11_12', '_12_1', '_1_2', 'all'),
                                      extra=days_in_month, max_num=days_in_month)
    regex = r'((' + month + r')[/]\d\d[/](' + year + r'))'
    initial_list = []
    for i in range(1, days_in_month):
        initial_list.append(data_dict[i])
    formset = DayFormSet(initial=initial_list,
                         queryset=volunteer.Days.all().filter(date__regex=regex))
    return DayFormSet, volunteer, formset, month
