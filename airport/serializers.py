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
    airplane_type = AirplaneTypeSerializer(many=False, read_only=False)

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")

    @transaction.atomic
    def create(self, validated_data):
        airplane_type_data = validated_data.pop("airplane_type", None)

        airplane_type, _ = AirplaneType.objects.get_or_create(**airplane_type_data)

        airplane = Airplane.objects.create(
            airplane_type=airplane_type, **validated_data
        )

        return airplane

    @transaction.atomic
    def update(self, instance, validated_data):
        airplane_type_data = validated_data.pop("airplane_type", None)

        if airplane_type_data:
            for attr, value in airplane_type_data.items():
                setattr(instance.airplane_type, attr, value)
            instance.airplane_type.save()

        return super().update(instance, validated_data)


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer(many=False, read_only=False)
    airplane = AirplaneSerializer(many=False, read_only=False)
    crew = CrewSerializer(many=True, read_only=False)

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")

    @transaction.atomic
    def create(self, validated_data):
        route_data = validated_data.pop("route", None)
        airplane_data = validated_data.pop("airplane", None)
        airplane_type_data = airplane_data.pop("airplane_type", None)
        crew_data = validated_data.pop("crew", [])

        route, _ = Route.objects.get_or_create(**route_data)

        airplane_type, _ = AirplaneType.objects.get_or_create(**airplane_type_data)
        airplane, _ = Airplane.objects.get_or_create(
            airplane_type=airplane_type, **airplane_data
        )

        crew_members = []
        for crew_member_data in crew_data:
            crew_member, _ = Crew.objects.get_or_create(**crew_member_data)
            crew_members.append(crew_member)

        flight = Flight.objects.create(route=route, airplane=airplane, **validated_data)
        flight.crew.set(crew_members)

        return flight

    @transaction.atomic
    def update(self, instance, validated_data):
        route_data = validated_data.pop("route", None)
        airplane_data = validated_data.pop("airplane", None)
        crew_data = validated_data.pop("crew", None)

        if route_data:
            for attr, value in route_data.items():
                setattr(instance.route, attr, value)
            instance.route.save()

        if airplane_data:
            airplane_type_data = airplane_data.pop("airplane_type", None)

            if airplane_type_data:
                for attr, value in airplane_type_data.items():
                    setattr(instance.airplane.airplane_type, attr, value)
                instance.airplane.airplane_type.save()

            for attr, value in airplane_data.items():
                setattr(instance.airplane, attr, value)
            instance.airplane.save()

        if crew_data is not None:
            crew_members = []
            for crew_member_data in crew_data:
                crew_member, _ = Crew.objects.get_or_create(**crew_member_data)
                crew_members.append(crew_member)
            instance.crew.set(crew_members)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "created_at", "user")


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()
    order = OrderSerializer()

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight", "order")
