from django.db import transaction
from rest_framework import serializers

from airport.models import (
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = AirportSerializer(many=False, read_only=False)
    destination = AirportSerializer(many=False, read_only=False)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")

    @transaction.atomic
    def create(self, validated_data):
        source_data = validated_data.pop("source", None)
        destination_data = validated_data.pop("destination", None)

        source_airport, _ = Airport.objects.get_or_create(**source_data)
        destination_airport, _ = Airport.objects.get_or_create(**destination_data)

        route = Route.objects.create(
            source=source_airport, destination=destination_airport, **validated_data
        )
        return route

    @transaction.atomic
    def update(self, instance, validated_data):
        source_data = validated_data.pop("source", None)
        destination_data = validated_data.pop("destination", None)

        if source_data:
            for attr, value in source_data.items():
                setattr(instance.source, attr, value)
            instance.source.save()

        if destination_data:
            for attr, value in destination_data.items():
                setattr(instance.destination, attr, value)
            instance.destination.save()

        return super().update(instance, validated_data)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False, read_only=True)
    airplane = AirplaneSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
