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
# App imports
from .models import Volunteer, SurveyStatus, Day
from .methods import check_time,  get_timeframes, check_age, appointment_conflict
from .forms import DayForm


def sync_galaxy(vol_data, check_list):
    for i in vol_data['data']:
        galaxy_id = int(i['id'])
        if galaxy_id in check_list:
            volunteer = Volunteer.objects.filter(galaxy_id=galaxy_id)
            print(volunteer)
            # Flag to skip updating if unsubscribed is true
            if not volunteer[0].unsubscribed:
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
    for volunteer in potential_list:
        if volunteer['dob'] != None and check_age(volunteer['dob']):
            volunteer['minor'] = True
        else:
            volunteer['minor'] = False
    for volunteer in potential_list:
        set_minor = Volunteer.objects.get(id=volunteer['id'])
        if set_minor.dob != None and check_age(set_minor.dob):
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
                from_email = 'acc.scheduler.care@gmail.com'
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
        from_email = 'acc.scheduler.care@gmail.com'
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


def send_monthly_surveys(request):
    sent_status = False
    dt = datetime.today()
    curr_month = dt.month
    curr_year = dt.year
    survey_month = curr_month + 1
    if survey_month == 13:
        survey_year = curr_year + 1
        survey_month = 1
    else:
        survey_year = curr_year
        survey_month = curr_month + 1

    if SurveyStatus.objects.filter(month=curr_month).filter(year=curr_year).count() == 0:
        survey_month = curr_month
        survey_year = curr_year
        survey = SurveyStatus.objects.create(month=curr_month, year=curr_year, sent=False)
    elif SurveyStatus.objects.filter(month=survey_month).filter(year=survey_year).count() == 0:
        survey = SurveyStatus.objects.create(month=survey_month, year=survey_year, sent=False)
        # survey = SurveyStatus.objects.get(survey_id=1)
    else:
        return sent_status, survey_month

    sent_status = True
    domain = get_current_site(request).domain
    invalid_emails = []
    invalid_phone = []

    for i in Volunteer.objects.all():
        token = get_random_string(length=32)
        i.survey_token = token
        activate_url = 'http://' + domain + "/survey_page" + "/?id=" + str(i.id) + "&month=" + str(survey_month) + "&year=" + str(survey_year) +  "&email=" + i.email \
                       + "&token=" + token
        if i.notify_email:
            email_subject = 'Volunteer Availability Survey'
            email_message = "Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                            "If you do not fill out the survey, your previous times will be carried over for the next month. " \
                            "Your time is so appreciated and we could not provide seniors with free programs without you!" \
                            "\n" + activate_url + "\n\nSincerely,\nSenior Escort Program Staff"
            from_email = 'acc.scheduler.care@gmail.com'
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
                    body="Hello Volunteer!\n\nPlease fill out the survey to provide your availability for the next month. " \
                         f"If you do not fill out the survey, your previous times will be carried over for the next month. "
                         f"Your time is so appreciated and we could not provide seniors with free programs without you!"
                         f"\n{activate_url}\n\nSincerely,\nSenior Escort Program Staff",
                    from_='+19569486977', to=i.phone)
            except TwilioException:
                print(f"{i.phone} is not a valid phone number.")
                invalid_phone.append(i.first_name + " " + i.last_name)

            print("to phone", i.phone)
        i.survey_token = token
        i.save()
        # survey.month = curr_month
    survey.sent = True
    survey.save()
    return sent_status, survey_month, invalid_emails, invalid_phone


def read_survey_data(option_list, volunteer, month, year):
    for i in range(1, 32):
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


def generate_v_days(pk, month, curr_year):
    volunteer = Volunteer.objects.get(id=pk)
    if month < 10:
        month = '0' + str(month)
    else:
        month = str(month)
    curr_year = str(curr_year)
    try:
        day1 = volunteer.Days.get(date=month + '/' + '01' + '/' + curr_year)
    except Day.DoesNotExist:
        for i in range(1, 32):
            if i < 10:
                day = '0' + str(i)
            else:
                day = str(i)
            Day.objects.create(_9_10=False, _10_11=False, _11_12=False, _12_1=False, _1_2=False, all=False,
                               date=month + '/' + day + '/' + curr_year, volunteer=volunteer)
        day1 = volunteer.Days.get(date=month + '/' + '01' + '/' + curr_year)
    day1 = volunteer.Days.get(date=month + '/' + '01' + '/' + curr_year)
    day2 = volunteer.Days.get(date=month + '/' + '02' + '/' + curr_year)
    day3 = volunteer.Days.get(date=month + '/' + '03' + '/' + curr_year)
    day4 = volunteer.Days.get(date=month + '/' + '04' + '/' + curr_year)
    day5 = volunteer.Days.get(date=month + '/' + '05' + '/' + curr_year)
    day6 = volunteer.Days.get(date=month + '/' + '06' + '/' + curr_year)
    day7 = volunteer.Days.get(date=month + '/' + '07' + '/' + curr_year)
    day8 = volunteer.Days.get(date=month + '/' + '08' + '/' + curr_year)
    day9 = volunteer.Days.get(date=month + '/' + '09' + '/' + curr_year)
    day10 = volunteer.Days.get(date=month + '/' + '10' + '/' + curr_year)
    day11 = volunteer.Days.get(date=month + '/' + '11' + '/' + curr_year)
    day12 = volunteer.Days.get(date=month + '/' + '12' + '/' + curr_year)
    day13 = volunteer.Days.get(date=month + '/' + '13' + '/' + curr_year)
    day14 = volunteer.Days.get(date=month + '/' + '14' + '/' + curr_year)
    day15 = volunteer.Days.get(date=month + '/' + '15' + '/' + curr_year)
    day16 = volunteer.Days.get(date=month + '/' + '16' + '/' + curr_year)
    day17 = volunteer.Days.get(date=month + '/' + '17' + '/' + curr_year)
    day18 = volunteer.Days.get(date=month + '/' + '18' + '/' + curr_year)
    day19 = volunteer.Days.get(date=month + '/' + '19' + '/' + curr_year)
    day20 = volunteer.Days.get(date=month + '/' + '20' + '/' + curr_year)
    day21 = volunteer.Days.get(date=month + '/' + '21' + '/' + curr_year)
    day22 = volunteer.Days.get(date=month + '/' + '22' + '/' + curr_year)
    day23 = volunteer.Days.get(date=month + '/' + '23' + '/' + curr_year)
    day24 = volunteer.Days.get(date=month + '/' + '24' + '/' + curr_year)
    day25 = volunteer.Days.get(date=month + '/' + '25' + '/' + curr_year)
    day26 = volunteer.Days.get(date=month + '/' + '26' + '/' + curr_year)
    day27 = volunteer.Days.get(date=month + '/' + '27' + '/' + curr_year)
    day28 = volunteer.Days.get(date=month + '/' + '28' + '/' + curr_year)
    day29 = volunteer.Days.get(date=month + '/' + '29' + '/' + curr_year)
    day30 = volunteer.Days.get(date=month + '/' + '30' + '/' + curr_year)
    day31 = volunteer.Days.get(date=month + '/' + '31' + '/' + curr_year)

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
    data10 = {'_9_10': day10._9_10, '_10_11': day10._10_11, '_11_12': day10._11_12, '_12_1': day10._12_1,
              '_1_2': day10._1_2,
              'all': day10.all}
    data11 = {'_9_10': day11._9_10, '_10_11': day11._10_11, '_11_12': day11._11_12, '_12_1': day11._12_1,
              '_1_2': day11._1_2,
              'all': day11.all}
    data12 = {'_9_10': day12._9_10, '_10_11': day12._10_11, '_11_12': day12._11_12, '_12_1': day12._12_1,
              '_1_2': day12._1_2,
              'all': day12.all}
    data13 = {'_9_10': day13._9_10, '_10_11': day13._10_11, '_11_12': day13._11_12, '_12_1': day13._12_1,
              '_1_2': day13._1_2,
              'all': day13.all}
    data14 = {'_9_10': day14._9_10, '_10_11': day14._10_11, '_11_12': day14._11_12, '_12_1': day14._12_1,
              '_1_2': day14._1_2,
              'all': day1.all}
    data15 = {'_9_10': day15._9_10, '_10_11': day15._10_11, '_11_12': day15._11_12, '_12_1': day15._12_1,
              '_1_2': day15._1_2,
              'all': day15.all}
    data16 = {'_9_10': day16._9_10, '_10_11': day16._10_11, '_11_12': day16._11_12, '_12_1': day16._12_1,
              '_1_2': day16._1_2,
              'all': day16.all}
    data17 = {'_9_10': day17._9_10, '_10_11': day17._10_11, '_11_12': day17._11_12, '_12_1': day17._12_1,
              '_1_2': day17._1_2,
              'all': day17.all}
    data18 = {'_9_10': day18._9_10, '_10_11': day18._10_11, '_11_12': day18._11_12, '_12_1': day18._12_1,
              '_1_2': day18._1_2,
              'all': day18.all}
    data19 = {'_9_10': day19._9_10, '_10_11': day19._10_11, '_11_12': day19._11_12, '_12_1': day19._12_1,
              '_1_2': day19._1_2,
              'all': day19.all}
    data20 = {'_9_10': day20._9_10, '_10_11': day20._10_11, '_11_12': day20._11_12, '_12_1': day20._12_1,
              '_1_2': day20._1_2,
              'all': day20.all}
    data21 = {'_9_10': day21._9_10, '_10_11': day21._10_11, '_11_12': day21._11_12, '_12_1': day21._12_1,
              '_1_2': day21._1_2,
              'all': day21.all}
    data22 = {'_9_10': day22._9_10, '_10_11': day22._10_11, '_11_12': day22._11_12, '_12_1': day22._12_1,
              '_1_2': day22._1_2,
              'all': day22.all}
    data23 = {'_9_10': day23._9_10, '_10_11': day23._10_11, '_11_12': day23._11_12, '_12_1': day23._12_1,
              '_1_2': day23._1_2,
              'all': day23.all}
    data24 = {'_9_10': day24._9_10, '_10_11': day24._10_11, '_11_12': day24._11_12, '_12_1': day24._12_1,
              '_1_2': day24._1_2,
              'all': day24.all}
    data25 = {'_9_10': day25._9_10, '_10_11': day25._10_11, '_11_12': day25._11_12, '_12_1': day25._12_1,
              '_1_2': day25._1_2,
              'all': day25.all}
    data26 = {'_9_10': day26._9_10, '_10_11': day26._10_11, '_11_12': day26._11_12, '_12_1': day26._12_1,
              '_1_2': day26._1_2,
              'all': day26.all}
    data27 = {'_9_10': day27._9_10, '_10_11': day27._10_11, '_11_12': day27._11_12, '_12_1': day27._12_1,
              '_1_2': day27._1_2,
              'all': day27.all}
    data28 = {'_9_10': day28._9_10, '_10_11': day28._10_11, '_11_12': day28._11_12, '_12_1': day28._12_1,
              '_1_2': day28._1_2,
              'all': day28.all}
    data29 = {'_9_10': day29._9_10, '_10_11': day29._10_11, '_11_12': day29._11_12, '_12_1': day29._12_1,
              '_1_2': day29._1_2,
              'all': day29.all}
    data30 = {'_9_10': day30._9_10, '_10_11': day30._10_11, '_11_12': day30._11_12, '_12_1': day30._12_1,
              '_1_2': day30._1_2,
              'all': day30.all}
    data31 = {'_9_10': day31._9_10, '_10_11': day31._10_11, '_11_12': day31._11_12, '_12_1': day31._12_1,
              '_1_2': day31._1_2,
              'all': day31.all}

    # current_month = datetime.now().strftime('%m')
    DayFormSet = modelformset_factory(Day, DayForm, fields=('_9_10', '_10_11', '_11_12', '_12_1', '_1_2', 'all'),
                                      extra=31, max_num=31)
    regex = r'((' + month + r')[/]\d\d[/](' + curr_year + r'))'
    formset = DayFormSet(initial=[data1, data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12,
                                  data13, data14, data15, data16, data17, data18, data19, data20, data21, data22,
                                  data23,
                                  data24, data25, data26, data27, data28, data29, data30, data31],
                         queryset=volunteer.Days.all().filter(date__regex=regex))
    return DayFormSet, volunteer, formset, month
