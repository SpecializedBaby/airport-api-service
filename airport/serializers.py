from rest_framework import serializers
from django.db import transaction

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order, Ticket


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city", "image"]


class AirportImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "image"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class RouteListSerializer(RouteSerializer):
    source = serializers.CharField(source="source.name", read_only=True)
    destination = serializers.CharField(source="destination.name", read_only=True)


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class RouteCleanSerializer(RouteListSerializer):
    class Meta:
        model = Route
        fields = ["source", "destination"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type", "capacity"]


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(source="airplane_type.name", read_only=True)


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crews"]


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(source="route.source")
    destination = serializers.CharField(source="route.destination")
    airplane = serializers.CharField(source="airplane.name", read_only=True)
    crews = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = ["id", "source", "destination", "airplane", "departure_time", "arrival_time", "crews", "tickets_available", ]


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_place(
            attrs["row"],
            attrs["seat"],
            attrs["flight"],
            serializers.ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]


class TicketListSerializer(TicketSerializer):
    flight = FlightListSerializer(many=False, read_only=True)


class TicketPlacesSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ["seat", "row"]


class FlightDetailSerializer(FlightSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = AirplaneListSerializer(many=False, read_only=True)
    crews = CrewSerializer(many=True, read_only=True)
    taken_places = TicketPlacesSerializer(many=True, read_only=True, source="tickets")

    class Meta:
        model = Flight
        fields = ["id", "route", "airplane", "departure_time", "arrival_time", "crews", "taken_places", ]


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ["id", "tickets", "created_at"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
