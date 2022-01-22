from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ test the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creatung user with valid payload is succesful"""
        payload = {
              "email": "test@user.com",
              "password": "test123",
              "name": "testname"

        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload["password"]))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """ Test creatung user that already exist fails"""
        payload = {
              "email": "test@user.com",
              "password": "test123",
              "name": "testname"

        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """ Test that the password must be more than 5 characters"""
        payload = {
              "email": "test@user.com",
              "password": "123",
              "name": "testname"

        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload["email"]
            ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test that a token is created for the user"""
        payload = {
                  "email": "test@user.com",
                  "password": "test123",
                  "name": "testname"

            }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ test that token is not created if invalid credentials are given"""
        payload = {
                  "email": "test@user.com",
                  "password": "test123",
                  "name": "testname"

            }
        create_user(email="test@user.com", password="test12345")
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """test that token is not created if user doesn't exist"""
        payload = {
                      "email": "test@user.com",
                      "password": "test123",
                      "name": "testname"

                }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """test that token is not created if user doesn't exist"""
        payload = {
                      "email": "onem",
                      "password": "",
                      "name": "testname"

                }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

#    def test_retrieve_user_unauthorized(self):
#        """test that authentication is required for users"""
#        res = self.client.get(ME_URL)

#        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPiTests(TestCase):
    """ Test API request that require authentification"""

    def setUp(self):
        self.user = create_user(
            email="test@user.com",
            password="test12345",
            name="name"
            )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """test retriving profile for logged in used"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email
            }
        )

#    def test_post_not_allowed(self):
#        """test that POST is not allowed on the me url"""
#        res = self.client.get(ME_URL, {})
#        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updateing the user profile for authentificated user"""
        payload = {
                      "email": "demo@user.com",
                      "password": "test123",
                      "name": "testdemo"

                }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload["name"])
        self.assertTrue(self.user.check_password(payload["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
