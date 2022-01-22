from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicTagsApiTests(TestCase):
    """test the publicly availavble tags API"""

    def setUp(self):
        self.client = APIClient()

#    def test_login_required(self):
#        """ test that login is required for retrieving tags"""
#        res = self.client.get(TAGS_URL)

#        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """test the authorized user tags tags API"""

    def setUp(self):
        self.user = create_user(
                    email="test@user.com",
                    password="test12345",
                    name="name"
                    )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name="Dessert")

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test that tags returned are for the authenticated user"""
        user2 = create_user(email='other@test.com', password="test123")
        Tag.objects.create(user=user2, name="Vegan")
        tag = Tag.objects.create(user=self.user, name="mcdo")

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'],tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': "test tag"}
        self.client.post(TAGS_URL, payload)
        res = self.client.get(TAGS_URL)
        exists = Tag.objects.filter(
                user=self.user,
                name=payload['name']
                ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Test creating a new tag"""
        payload = {'name': ""}
        res = self.client.post(TAGS_URL, payload)

        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
