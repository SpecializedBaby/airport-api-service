from django.core.exceptions import ValidationError
from django.db import models

from airport_service import settings


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departing_routes")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="arriving_routes")
    distance = models.IntegerField()

    def __str__(self):
        return self.source.name + " - " + self.destination.name


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE, related_name="airplanes")

    def __str__(self):
        return self.name + " " + self.airplane_type.name

    @property
    def capacity(self):
        return self.rows * self.seats_in_row


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crews = models.ManyToManyField(Crew)

    class Meta:
        ordering = ["-departure_time"]

    def __str__(self):
        return str(self.route) + " " + str(self.departure_time)


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_place(row, seat, flight, error_to_raise):
        for ticket_attr_value, ticket_attr_name, flight_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            count_attrs = getattr(
                flight.airplane, flight_attr_name
            )
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {flight_attr_name}): "
                        f"(1, {count_attrs})"
                    }

                )

    def clean(self):
        Ticket.validate_place(
            self.row,
            self.seat,
            self.flight,
            ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"

    class Meta:
        unique_together = ["flight", "row", "seat"]
