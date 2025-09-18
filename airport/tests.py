from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight

User = get_user_model()


class FlightAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", password="testcase"
        )
        self.client.force_authenticate(user=self.user)

        self.airport = Airport.objects.create(
            name="Test Airport", closest_big_city="Test City"
        )
        self.route = Route.objects.create(
            source=self.airport, destination=self.airport, distance=150
        )
        self.airplane_type = AirplaneType.objects.create(name="Boeing 747")
        self.airplane = Airplane.objects.create(
            name="Test Plane", airplane_type=self.airplane_type, rows=11, seats_in_row=8
        )
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2025-09-18T10:00:00Z",
            arrival_time="2025-09-18T12:00:00Z",
        )
        self.flight.crew.add(self.crew)

        self.url = reverse("airport:flight-list")

    def test_list_flights(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_filter_flights_by_route(self):
        response = self.client.get(self.url, {"route": self.route.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["route"]["id"], self.route.id)

    def test_ordering_flights_desc(self):
        flight2 = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time="2025-09-18T14:00:00Z",
            arrival_time="2025-09-18T16:00:00Z",
        )

        response = self.client.get(self.url, {"ordering": "-departure_time"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["id"], flight2.id)
        self.assertEqual(response.data["results"][1]["id"], self.flight.id)

    def test_search_flights_by_airplane_name(self):
        response = self.client.get(self.url, {"search": "Test Plane"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"][0]["airplane"]["id"], self.airplane.id
        )


class PermissionsAPITest(APITestCase):
    def setUp(self):
        self.airport_data = {"name": "Test Airport", "closest_big_city": "Test City"}

        self.user = User.objects.create_user(email="user@test.com", password="test123")
        self.admin = User.objects.create_user(
            email="admin@test.com", password="admin123", is_staff=True
        )

        self.url = reverse("airport:airport-list")

    def test_anonymous_user_cannot_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_get(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_cannot_post(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.airport_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_post(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(self.url, self.airport_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_get(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
