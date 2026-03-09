from django.test import TestCase
from apps.registrations.models import Registration
from apps.registrations.forms import RegistrationForm
import datetime

class RegistrationTestCase(TestCase):
    def test_registration_whatsapp_formatted(self):
        reg = Registration(whatsapp="11999999999")
        self.assertEqual(reg.whatsapp_formatted, "5511999999999@c.us")
        
        reg2 = Registration(whatsapp="5511988888888")
        self.assertEqual(reg2.whatsapp_formatted, "5511988888888@c.us")

    def test_cpf_masking(self):
        reg = Registration(cpf="12345678901")
        self.assertEqual(reg.cpf_masked, "123.***.***-01")

    def test_form_invalid_cpf(self):
        form_data = {
            "full_name": "Test User",
            "birth_date": "1990-01-01",
            "email": "test@example.com",
            "whatsapp": "11999999999",
            "rg": "123456",
            "cpf": "111.111.111-11", # Invalid
            "address": "Street X",
            "course_name": "Course Y",
            "city": "City Z",
            "state": "SP",
            "course_workload": 8,
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("cpf", form.errors)
