from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testcase"
        )

    def test_successful_register_user(self):
        response = self.client.post(
            reverse("user:register"),
            data={"email": "unique_test@gmail.com", "password": "testtest"},
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_user_fails_with_duplicate_email(self):
        response = self.client.post(
            reverse("user:register"),
            data={"email": "test@gmail.com", "password": "testcase"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_fails_with_incorrect_password(self):
        response = self.client.post(
            reverse("user:register"),
            data={"email": "unique_test@gmail.com", "password": ""},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_user_can_access_manage_endpoint(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse("user:manage"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_user_cannot_access_manage_endpoint(self):
        response = self.client.get(reverse("user:manage"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_obtain_jwt_token(self):
        response = self.client.post(
            reverse("user:token_obtain_pair"),
            data={"email": "test@gmail.com", "password": "testcase"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_access_protected_view_with_jwt(self):
        token_response = self.client.post(
            reverse("user:token_obtain_pair"),
            data={"email": "test@gmail.com", "password": "testcase"},
        )
        token_access = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_access}")

        page_response = self.client.get(reverse("user:manage"))

        self.assertEqual(page_response.status_code, status.HTTP_200_OK)

    def test_token_refresh(self):
        token_response = self.client.post(
            reverse("user:token_obtain_pair"),
            data={"email": "test@gmail.com", "password": "testcase"},
        )
        token = token_response.data["refresh"]

        page_response = self.client.post(
            reverse("user:token_refresh"), data={"refresh": token}
        )

        self.assertEqual(page_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", page_response.data)
