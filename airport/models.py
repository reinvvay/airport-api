from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="routes_to"
    )
    distance = models.IntegerField()

    def clean(self):
        if self.source == self.destination:
            raise ValidationError("Source and destination airports must be different.")

    def __str__(self):
        return f"{self.source} ➝ {self.destination}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def clean(self):
        if (
            Crew.objects.filter(first_name=self.first_name, last_name=self.last_name)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError(
                "Crew member with this first and last name already exists."
            )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name_plural = "Crew"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def clean(self):
        if self.arrival_time <= self.departure_time:
            raise ValidationError("Arrival time must be after departure time.")

    def __str__(self):
        return f"{self.route}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.id} by {self.user.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    def clean(self):
        super().clean()

        airplane = self.flight.airplane
        if not (1 <= self.row <= airplane.rows):
            raise ValidationError(f"Row must be between 1 and {airplane.rows}.")
        if not (1 <= self.seat <= airplane.seats_in_row):
            raise ValidationError(
                f"Seat must be between 1 and {airplane.seats_in_row}."
            )

        if (
            Ticket.objects.filter(flight=self.flight, row=self.row, seat=self.seat)
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError("This seat is already taken on this flight.")

    def __str__(self):
        return f"Ticket: Row {self.row}, Seat {self.seat}, Flight {self.flight}"
