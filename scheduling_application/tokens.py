# UNUSED
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, appointment, timestamp):
        return (text_type(appointment.volunteer)+text_type(appointment.pk)+text_type(timestamp))
        # return (text_type(user.pk) + text_type(timestamp) + text_type(user.profile.email_confirmed))

appointment_confirmation_token = TokenGenerator()