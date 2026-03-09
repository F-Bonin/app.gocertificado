from django.test import TestCase
from apps.core.models import Company, Instructor

class CoreModelsTestCase(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12.345.678/0001-90"
        )
    
    def test_company_creation(self):
        self.assertEqual(self.company.name, "Test Company")
        self.assertEqual(str(self.company), "Test Company")

    def test_instructor_creation(self):
        instructor = Instructor.objects.create(
            company=self.company,
            full_name="John Doe",
            credentials="Expert"
        )
        self.assertEqual(instructor.full_name, "John Doe")
        self.assertIn("John Doe", str(instructor))
