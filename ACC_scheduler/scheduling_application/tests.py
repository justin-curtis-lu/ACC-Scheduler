from django.test import TestCase
from django.urls import reverse
from .models import Senior, Volunteer


class MakeAppointmentViewTests(TestCase):

    def test_view_url_exists(self):
        response = self.client.get('/make_appointment/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'scheduling_application/make_appointment/make_appointment.html')

    def test_no_seniors(self):
        """
        If no seniors exist, an appropriate message is displayed
        """
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No participants currently added.")
        self.assertQuerysetEqual(response.context['seniors_list'], [])

    def test_no_volunteers(self):
        """
        If no volunteers exist, an appropriate message is displayed
        """
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No volunteers currently added.")
        self.assertQuerysetEqual(response.context['volunteers_list'], [])

    def test_seniors_in_database(self):
        """
        If there are seniors in the database, an appropriate message is displayed
        """
        test_senior = Senior.objects.create(last_name="Doe", first_name="Jane", vaccinated=True, notify_email=False,
                                            notify_text=False, notify_call=True)
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Participants currently in the database")
        self.assertGreaterEqual(len(response.context['seniors_list']), 1)

    def test_volunteers_in_database(self):
        """
        If there are volunteers in the database, an appropriate message is displayed
        """
        test_volunteer = Volunteer.objects.create(last_name="Yeo", first_name="Nate", minor=False, vaccinated=True,
                                                  notify_email=False, notify_text=False, notify_call=True)
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Volunteers currently in the database")
        self.assertGreaterEqual(len(response.context['volunteers_list']), 1)

    def test_no_available_volunteers(self):
        """
        If there are no available volunteers for the specified time, appropriate message is displayed
        """
        response = self.client.get(reverse('make_appointment'))
        print(response.context['potential_list'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No volunteers are available at this time.")
        self.assertQuerySetEqual(response.context['potential_list'], [])

    # idk what to do
    def test_correct_datetime_format(self):
        """
        If datetime format is incorrect, display appropriate message
        """
        day_time = "asklhgli"
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please input date and time in the format 'MM/DD/YYYY XX:XX-YY:YY'.")
        #self.assertQuerysetEqual(response.get, ["hello"])


#class SeniorPageTests(TestCase):

