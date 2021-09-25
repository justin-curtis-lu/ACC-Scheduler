from django.test import TestCase
from django.urls import reverse
from .models import Senior, Volunteer
import requests


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
        self.assertQuerysetEqual(response.context['seniors_list'], [])

    def test_no_volunteers(self):
        """
        If no volunteers exist, volunteers_list should be empty
        """
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['volunteers_list'], [])

    def test_seniors_in_database(self):
        """
        If there are seniors in the database, there should be items in seniors_list
        """
        test_senior = Senior.objects.create(last_name="Doe", first_name="Jane", vaccinated=True, notify_email=False,
                                            notify_text=False, notify_call=True)
        response = self.client.get(reverse('make_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.context['seniors_list']), 1)


    #def test_correct_datetime_format(self):
    #    """
    #    If datetime format is incorrect, display appropriate message
    #    """
    #    day_time = "asklhgli"
    #    good_daytime = "04/03/2000"
    #    response = self.client.get(reverse('make_appointment'))
    #    self.assertEqual(response.status_code, 200)
    #    response = requests.post("http://127:0:0:1/make_appointment", {''})
    #    print()
    #    print(response)
    #    # self.assertContains(response, "Please input date and time in the format 'MM/DD/YYYY XX:XX-YY:YY'.")
    #    #self.assertQuerysetEqual(response.get, ["hello"])


