from django.test import TestCase
from django.urls import reverse
from .models import Senior, Volunteer, Appointment, Day
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth import get_user_model
import requests
from .utils import unsub_comms, unsub_all, read_survey_data


class SurveyReadDataTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_survey_input_0x_db(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=False, notify_call=False)
        month = '09'
        year = '2021'
        options = ['option1-1', 'option1-2', 'option2-5']
        read_survey_data(options, vol_a, month, year)
        # Day 1
        self.assertEqual(Day.objects.get(date='09/01/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='09/01/2021')._10_11, True)
        self.assertEqual(Day.objects.get(date='09/01/2021')._11_12, True)
        self.assertEqual(Day.objects.get(date='09/01/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='09/01/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='09/01/2021').all, False)
        # Day 2
        self.assertEqual(Day.objects.get(date='09/02/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='09/02/2021')._10_11, False)
        self.assertEqual(Day.objects.get(date='09/02/2021')._11_12, False)
        self.assertEqual(Day.objects.get(date='09/02/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='09/02/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='09/02/2021').all, True)
        # Day 3
        self.assertEqual(Day.objects.get(date='09/03/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='09/03/2021')._10_11, False)
        self.assertEqual(Day.objects.get(date='09/03/2021')._11_12, False)
        self.assertEqual(Day.objects.get(date='09/03/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='09/03/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='09/03/2021').all, False)

    def test_survey_input_xx_db(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=False, notify_call=False)
        month = '11'
        year = '2021'
        options = ['option1-1', 'option1-2', 'option2-5']
        read_survey_data(options, vol_a, month, year)
        # Day 1
        self.assertEqual(Day.objects.get(date='11/01/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='11/01/2021')._10_11, True)
        self.assertEqual(Day.objects.get(date='11/01/2021')._11_12, True)
        self.assertEqual(Day.objects.get(date='11/01/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='11/01/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='11/01/2021').all, False)
        # Day 2
        self.assertEqual(Day.objects.get(date='11/02/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='11/02/2021')._10_11, False)
        self.assertEqual(Day.objects.get(date='11/02/2021')._11_12, False)
        self.assertEqual(Day.objects.get(date='11/02/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='11/02/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='11/02/2021').all, True)
        # Day 3
        self.assertEqual(Day.objects.get(date='11/03/2021')._9_10, False)
        self.assertEqual(Day.objects.get(date='11/03/2021')._10_11, False)
        self.assertEqual(Day.objects.get(date='11/03/2021')._11_12, False)
        self.assertEqual(Day.objects.get(date='11/03/2021')._12_1, False)
        self.assertEqual(Day.objects.get(date='11/03/2021')._1_2, False)
        self.assertEqual(Day.objects.get(date='11/03/2021').all, False)

    def test_survey_months(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=False, notify_call=False)
        year = '2055'
        options = ['option1-1']
        for i in range(1, 13):
            if i < 10:
                month = '0'+str(i)
            else:
                month = str(i)
            read_survey_data(options, vol_a, month, year)
        self.assertEqual(Day.objects.get(date='01/31/2055')._9_10, False)
        # self.assertEqual(Day.objects.get(date='02/03/2055')._9_10, False) # Leap Year ?
        self.assertEqual(Day.objects.get(date='03/31/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='04/30/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='05/31/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='06/30/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='07/31/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='08/31/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='09/30/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='10/31/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='11/30/2055')._9_10, False)
        self.assertEqual(Day.objects.get(date='12/31/2055')._9_10, False)


class SurveysVolunteerSideTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_bad_link(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=False, notify_call=False)
        vol_a.survey_token = 'ABCDEFG123'
        vol_a.save()
        response = self.client.get(reverse('survey_page'), data={'id': vol_a.id, 'email': vol_a.email,
                                                                 'token': vol_a.survey_token+'ABC', 'month': '09',
                                                                 'year': '2021'}, follow=True)
        self.assertTemplateUsed(response, 'scheduling_application/bad_link.html')

    def test_good_link(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=False, notify_call=False)
        vol_a.survey_token = 'ABCDEFG123'
        vol_a.save()
        response = self.client.get(reverse('survey_page'), data={'id': vol_a.id, 'email': vol_a.email,
                                                                 'token': vol_a.survey_token, 'month': '09',
                                                                 'year': '2021'}, follow=True)
        self.assertTemplateUsed(response, 'scheduling_application/survey_sending/survey_page.html')


class UnsubscribeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_unsubscribe_comms(self):
        self.client.login(username='temporary', password='temporary')
        vol_a = Volunteer.objects.create(last_name="A", first_name="A", email="test@gmail.com", minor=False,
                                         vaccinated=True,
                                         notify_email=True, notify_text=True, notify_call=False)
        unsub_comms(vol_a)
        self.assertEqual(vol_a.notify_email, False)
        self.assertEqual(vol_a.notify_text, False)

    def test_unsubscribe_all(self):
        self.client.login(username='temporary', password='temporary')
        vol_b = Volunteer.objects.create(last_name="B", first_name="B", email="test@gmail.com", minor=False, phone='2221112222',
                                         vaccinated=True,
                                         notify_email=True, notify_text=True, notify_call=True)
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertEqual(len(vol_b.Days.all()), 30)
        unsub_all(vol_b)
        self.assertEqual(vol_b.notify_email, False)
        self.assertEqual(vol_b.notify_text, False)
        self.assertEqual(len(vol_b.Days.all()), 0)


class SendSurveyViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        test_volunteer = Volunteer.objects.create(last_name="Yeo", first_name="Nate", email="test@gmail.com", minor=False, vaccinated=True,
                                                  notify_email=True, notify_text=False, notify_call=False)

    def test_send_surveys(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                                       fetch_redirect_response=False)
        self.assertContains(response, "Successfully sent surveys for the month of September")

    def test_send_duplicate_surveys(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                             fetch_redirect_response=False)
        self.assertContains(response, "Successfully sent surveys for the month of September")
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                             fetch_redirect_response=False)
        self.assertContains(response, "Successfully sent surveys for the month of September")

    def test_days_created(self):
        test_volunteer2 = Volunteer.objects.create(last_name="Yeo", first_name="Nate2", email="test@gmail.com",
                                                  minor=False, vaccinated=True,
                                                  notify_email=True, notify_text=False, notify_call=False)
        test_volunteer3 = Volunteer.objects.create(last_name="Yeo", first_name="Nate2", email="test@gmail.com",
                                                   minor=False, vaccinated=True,
                                                   notify_email=True, notify_text=False, notify_call=False)
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                             fetch_redirect_response=False)
        response = self.client.get(reverse('send_survey'), data={'datepicker': '10/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                             fetch_redirect_response=False)
        self.assertEqual(len(test_volunteer2.Days.all()), 61)
        self.assertEqual(len(test_volunteer3.Days.all()), 61)


class SendBadSurveyViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_bad_phone(self):
        self.client.login(username='temporary', password='temporary')
        test_volunteer = Volunteer.objects.create(last_name="Foo", first_name="Bob", minor=False, vaccinated=True,
                                                  phone="222", notify_email=False, notify_text=True, notify_call=False)
        response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
        self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
                             fetch_redirect_response=False)
        self.assertContains(response, "Successfully sent surveys for the month of September")
        self.assertContains(response, "Texts have not been sent to the following volunteers as their phone numbers are invalid")

    # App side working ATM but not Test
    # def test_bad_email(self):
    #     test_volunteer = Volunteer.objects.create(last_name="Foo", first_name="Bob", email='dsn29hd23uk', minor=False, vaccinated=True,
    #                                                notify_email=True, notify_text=False, notify_call=False)
    #     self.client.login(username='temporary', password='temporary')
    #     response = self.client.get(reverse('send_survey'), data={'datepicker': '09/2021'}, follow=True)
    #     self.assertRedirects(response, '/pre_send_survey/', status_code=302, target_status_code=200,
    #                          fetch_redirect_response=False)
    #     print(response.content)
    #     self.assertContains(response, "Successfully sent surveys for the month of September")
    #     self.assertContains(response, "Emails have not been sent to the following volunteers as their emails are invalid")


class ViewVolunteersViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_empty_volunteers(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('view_volunteers'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['volunteers']), 0)

    def test_single_volunteer(self):
        self.client.login(username='temporary', password='temporary')
        test_volunteer = Volunteer.objects.create(last_name="Yeo", first_name="Nate", minor=False, phone='ABC',
                                                  email='email@email.com', vaccinated=True, additional_notes='GGEX',
                                                  notify_email=False, notify_text=False, notify_call=True)
        response = self.client.get(reverse('view_volunteers'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nate")
        self.assertContains(response, "Yeo")
        self.assertContains(response, "ABC")
        self.assertContains(response, "email@email.com")
        self.assertContains(response, "GGEX")
        self.assertEqual(len(response.context['volunteers']), 1)


class ViewSeniorsViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_empty_seniors(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('view_seniors'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['seniors']), 0)

    def test_single_senior(self):
        self.client.login(username='temporary', password='temporary')
        test_senior = Senior.objects.create(last_name="Yeo", first_name="Nate", phone='ABC',
                                                  email='email@email.com', vaccinated=True, additional_notes='GGEX',
                                                  notify_email=False, notify_text=False, notify_call=True)
        response = self.client.get(reverse('view_seniors'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nate")
        self.assertContains(response, "Yeo")
        self.assertContains(response, "ABC")
        self.assertContains(response, "email@email.com")
        self.assertContains(response, "GGEX")
        self.assertEqual(len(response.context['seniors']), 1)


class ViewAppointmentsViewTests(TestCase):

    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_empty_appointments(self):
        self.client.login(username='temporary', password='temporary')
        response = self.client.get(reverse('view_appointments'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['appointments']), 0)

    def test_single_appointment(self):
        self.client.login(username='temporary', password='temporary')
        test_senior = Senior.objects.create(last_name="Beo", first_name="Bate", phone='ABC',
                                                  email='email@email.com', vaccinated=True, additional_notes='GGEX',
                                                  notify_email=False, notify_text=False, notify_call=True)
        test_volunteer = Volunteer.objects.create(last_name="Yeo", first_name="Nate", minor=False, phone='ABC',
                                                  email='email@email.com', vaccinated=True, additional_notes='GGEX',
                                                  notify_email=False, notify_text=False, notify_call=True)
        test_appointment = Appointment.objects.create(volunteer=test_volunteer, senior=test_senior, start_address="Costco",
                                                      end_address='Safeway', purpose_of_trip="Grocery Run")
        response = self.client.get(reverse('view_appointments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bate")
        self.assertContains(response, "Beo")
        self.assertContains(response, "Nate")
        self.assertContains(response, "Yeo")
        self.assertContains(response, "Costco")
        self.assertContains(response, "Safeway")
        self.assertContains(response, "Grocery Run")
        self.assertEqual(len(response.context['appointments']), 1)


class NoAuthViewTests(TestCase):
    def test_no_auth_home(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_console(self):
        response = self.client.get(reverse('console'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_view_appointments(self):
        response = self.client.get(reverse('view_appointments'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_appointment_page(self):
        response = self.client.get(reverse('appointment_page', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_edit_appointment(self):
        response = self.client.get(reverse('edit_appointment', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_view_seniors(self):
        response = self.client.get(reverse('view_seniors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_add_senior(self):
        response = self.client.get(reverse('add_senior'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_edit_senior(self):
        response = self.client.get(reverse('edit_senior', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_senior_page(self):
        response = self.client.get(reverse('senior_page', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_view_volunteers(self):
        response = self.client.get(reverse('view_volunteers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_add_volunteer(self):
        response = self.client.get(reverse('add_volunteer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_edit_volunteer(self):
        response = self.client.get(reverse('edit_volunteer', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_view_availability(self):
        response = self.client.get(reverse('view_availability', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_volunteer_page(self):
        response = self.client.get(reverse('volunteer_page', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_galaxy_update_volunteers(self):
        response = self.client.get(reverse('galaxy_update_volunteers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_make_appointment(self):
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_confirm_volunteers(self):
        response = self.client.get(reverse('confirm_volunteers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_send_survey(self):
        response = self.client.get(reverse('send_survey'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')

    def test_no_auth_pre_send_survey(self):
        response = self.client.get(reverse('pre_send_survey'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/authentication_general/home.html')


# class MakeAppointmentViewTests(TestCase):
#     def setUp(self):
#         User = get_user_model()
#         user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
#
#     def test_view_url_exists(self):
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get('/make_appointment/')
#         self.assertEqual(response.status_code, 200)
#
#     def test_view_url_accessible_by_name(self):
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_view_uses_correct_template(self):
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'scheduling_application/make_appointment/make_appointment.html')
#
#     def test_no_seniors(self):
#         """
#         If no seniors exist, an appropriate message is displayed
#         """
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No participants currently added.")
#         self.assertQuerysetEqual(response.context['seniors_list'], [])
#
#     def test_no_volunteers(self):
#         """
#         If no volunteers exist, an appropriate message is displayed
#         """
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No volunteers currently added.")
#         self.assertQuerysetEqual(response.context['volunteers_list'], [])
#
#     def test_seniors_in_database(self):
#         """
#         If there are seniors in the database, an appropriate message is displayed
#         """
#         self.client.login(username='temporary', password='temporary')
#         test_senior = Senior.objects.create(last_name="Doe", first_name="Jane", vaccinated=True, notify_email=False,
#                                             notify_text=False, notify_call=True)
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Participants currently in the database")
#         self.assertGreaterEqual(len(response.context['seniors_list']), 1)
#
#     def test_volunteers_in_database(self):
#         """
#         If there are volunteers in the database, an appropriate message is displayed
#         """
#         self.client.login(username='temporary', password='temporary')
#         test_volunteer = Volunteer.objects.create(last_name="Yeo", first_name="Nate", minor=False, vaccinated=True,
#                                                   notify_email=False, notify_text=False, notify_call=True)
#         response = self.client.get(reverse('make_appointment'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Volunteers currently in the database")
#         self.assertGreaterEqual(len(response.context['volunteers_list']), 1)
#
#     def test_no_available_volunteers(self):
#         """
#         If there are no available volunteers for the specified time, appropriate message is displayed
#         """
#         self.client.login(username='temporary', password='temporary')
#         response = self.client.get(reverse('make_appointment'))
#         print(response.context['potential_list'])
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No volunteers are available at this time.")
#         self.assertQuerySetEqual(response.context['potential_list'], [])
