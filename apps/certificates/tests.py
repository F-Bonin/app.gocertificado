from django.test import TestCase
from apps.core.models import Company, Instructor
from apps.registrations.models import Registration
from apps.certificates.models import Certificate
import datetime

class CertificateTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name="Cert Test")
        self.instructor = Instructor.objects.create(
            company=self.company,
            full_name="Instructor 1",
            credentials="PhD"
        )
        self.registration = Registration.objects.create(
            full_name="Student Test",
            birth_date=datetime.date(1995, 1, 1),
            email="student@test.com",
            whatsapp="11999999999",
            rg="12345",
            cpf="123.456.789-01",
            address="Some address",
            course_name="Test Course",
            city="Test City",
            state="SP",
            course_workload=10,
            instructor=self.instructor
        )

    def test_certificate_creation_and_code(self):
        cert, created = Certificate.objects.get_or_create(registration=self.registration)
        self.assertTrue(created)
        self.assertEqual(len(cert.numeric_code), 12)
        self.assertIn(cert.numeric_code[:4], cert.numeric_code_formatted)

    def test_verification_url(self):
        cert = Certificate.objects.create(registration=self.registration)
        # Using the base URL from .env (usually http://localhost:8000 in dev)
        from django.conf import settings
        self.assertIn(settings.CERTIFICATE_BASE_URL, cert.verification_url)
        self.assertIn(cert.numeric_code, cert.verification_url)
