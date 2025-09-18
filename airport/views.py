from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets

from airport.models import (
    Airport,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
    Route,
)
from airport.permissions import IsAdminOrIfAuthenticatedReadOnly
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.select_related(
        "route__source", "route__destination", "airplane__airplane_type"
    ).prefetch_related("crew")
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    )
    search_fields = [
        "route__source__name",
        "route__destination__name",
        "airplane__name",
        "crew__first_name",
        "crew__last_name",
    ]
    ordering_fields = ["departure_time", "arrival_time", "route__source__name"]
    ordering = ["departure_time"]
    filterset_fields = ["route", "airplane"]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search by source airport name, destination airport name, airplane name, crew first or last name",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                name="ordering",
                description='Ordering by departure_time, arrival_time, or route source name. Prefix with "-" for descending order',
                type=OpenApiTypes.STR,
                enum=[
                    "departure_time",
                    "-departure_time",
                    "arrival_time",
                    "-arrival_time",
                    "route__source__name",
                    "-route__source__name",
                ],
            ),
            OpenApiParameter(
                name="route",
                description="Filter by route ID",
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="airplane",
                description="Filter by airplane ID",
                type=OpenApiTypes.INT,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of flights.

        Supports:
        - Search by source airport name, destination airport name, airplane name, crew names.
        - Filter by route ID and airplane ID.
        - Ordering by departure time, arrival time, or route source name.
        """
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user")
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related(
        "flight__route", "flight__airplane", "order__user"
    )
    serializer_class = TicketSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
