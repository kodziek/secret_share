from django.test import SimpleTestCase

from core.helpers import generate_random_password


class GenerateRandomPasswordTestCase(SimpleTestCase):
    def test_default_password_length(self):
        password = generate_random_password()
        self.assertEqual(len(password), 15)

    def test_specified_password_length(self):
        password_length = 5
        password = generate_random_password(password_length)
        self.assertEqual(len(password), password_length)

    def test_generated_passwords_differs(self):
        self.assertNotEqual(
            generate_random_password(), generate_random_password(),
        )
