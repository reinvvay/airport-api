from django.contrib import admin

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


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    search_fields = ("name", "closest_big_city")
    list_filter = ("name", "closest_big_city")
    ordering = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance")
    search_fields = ("source__name", "destination__name", "distance")
    list_filter = ("source", "destination")
    ordering = ("source",)


@admin.register(Crew)
class CrewAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
    search_fields = ("first_name", "last_name")
    list_filter = ("last_name", "first_name")
    ordering = ("last_name",)


@admin.register(AirplaneType)
class AirplaneTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    ordering = ("name",)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ("name", "rows", "seats_in_row", "airplane_type")
    search_fields = ("name", "rows", "seats_in_row", "airplane_type__name")
    list_filter = ("name", "airplane_type")
    ordering = ("name",)


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        "get_source",
        "get_destination",
        "get_airplane",
        "departure_time",
        "arrival_time",
        "get_crew",
    )
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "route__source__closest_big_city",
        "route__destination__closest_big_city",
        "airplane__name",
        "departure_time",
        "arrival_time",
        "crew__first_name",
        "crew__last_name",
    )
    list_filter = ("route", "airplane", "departure_time", "arrival_time", "crew")
    ordering = ("route__source__name",)

    def get_source(self, obj):
        return obj.route.source.name

    get_source.short_description = "Source"

    def get_destination(self, obj):
        return obj.route.destination.name

    get_destination.short_description = "Destination"

    def get_airplane(self, obj):
        return obj.airplane.name

    get_airplane.short_description = "Airplane"

    def get_crew(self, obj):
        return ", ".join(
            [f"{member.first_name} {member.last_name}" for member in obj.crew.all()]
        )

    get_crew.short_description = "Crew"


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__email",)
    list_filter = ("user__email", "created_at")
    ordering = ("-created_at",)
    inlines = (TicketInline,)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("flight", "row", "seat")
    search_fields = ("flight__airplane__name", "order__user__email")
    list_filter = ("flight", "row", "seat")
    ordering = ("order__user__email",)
