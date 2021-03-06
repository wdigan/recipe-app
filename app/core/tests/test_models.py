from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email="test@test.com", password="test123"):
    return  get_user_model().objects.create_user(
                email=email,
                password=password
                )

class ModelTests(TestCase):

    def test_create_user_with_email_successfull(self):
        """ test creating a new user with an email is
         test_create_user_with_email_successfull"""
        email = "test@test.com"
        password = "12345"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """ test the email for a new user is normalized"""
        email = "test@TEST.COM"
        user = get_user_model().objects.create_user(email, "test123")

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """ test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """test cratinf a new superuser"""
        user = get_user_model().objects.create_superuser(
            "test@superuser.com",
            "12345"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_st(self):
        """test the tag string representation"""
        tag = models.Tag.objects.create(
                user=sample_user(),
                name='Vegan'

        )
        self.assertEqual(str(tag), tag.name)
