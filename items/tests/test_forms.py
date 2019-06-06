from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase

from items.factories import ItemFactory
from items.forms import ItemForm, ItemAccessForm, ItemPasswordForm


class ItemFormTestCase(SimpleTestCase):
    def test_validation_missing_data(self):
        form = ItemForm({})
        self.assertFalse(form.is_valid())
        error_msg = 'One of following fields is required: url or file'
        with self.assertRaisesMessage(ValidationError, error_msg):
            form.clean()

    def test_validation_only_valid_url(self):
        data = {
            'url': 'http://kodziek.pl',
        }
        form = ItemForm(data)
        self.assertTrue(form.is_valid())

    def test_validation_invalid_url(self):
        data = {
            'url': 'invalid url',
        }
        form = ItemForm(data)
        self.assertFalse(form.is_valid())

    def test_validation_only_valid_file(self):
        files = {
            'file': SimpleUploadedFile('file', b'content'),
        }
        form = ItemForm(files=files)
        self.assertTrue(form.is_valid())

    def test_validation_invalid_file(self):
        files = {
            'file': 'invalid file',
        }
        form = ItemForm(files=files)
        self.assertFalse(form.is_valid())

    def test_validation_both_fields(self):
        data = {
            'url': 'http://kodziek.pl',
        }
        files = {
            'file': SimpleUploadedFile('file', b'content'),
        }
        form = ItemForm(data, files)
        self.assertFalse(form.is_valid())
        error_msg = 'Cannot use both fields (url and file) at the same time.'
        with self.assertRaisesMessage(ValidationError, error_msg):
            form.clean()


class ItemAccessFormTestCase(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        cls.password = 'pwd'
        cls.item = ItemFactory.build(password=make_password(cls.password))

    @classmethod
    def tearDownClass(cls):
        pass

    def test_validation_password_missing(self):
        form = ItemAccessForm(data={}, item=self.item)
        self.assertFalse(form.is_valid())

    def test_validation_password_incorrect(self):
        data = {
            'password': 'incorrect',
        }
        form = ItemAccessForm(data=data, item=self.item)
        self.assertFalse(form.is_valid())
        error_msg = 'Incorrect password.'
        with self.assertRaisesMessage(ValidationError, error_msg):
            form.clean()

    def test_validation_password_correct(self):
        data = {
            'password': self.password,
        }
        form = ItemAccessForm(data=data, item=self.item)
        self.assertTrue(form.is_valid())


class ItemPasswordFormTestCase(SimpleTestCase):
    def test_hashing_password(self):
        password = 'pwd'
        data = {
            'password': password,
        }
        form = ItemPasswordForm(data)
        self.assertTrue(form.is_valid())
        self.assertTrue(
            check_password(password, form.cleaned_data['password']),
        )
