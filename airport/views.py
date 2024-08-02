from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Q, Count, F
from datetime import datetime

from airport.models import Airport, Route, AirplaneType, Airplane, Crew, Flight, Order
from airport.pagination import OrderPagination
from airport.serializers import AirportSerializer, RouteSerializer, AirplaneTypeSerializer, AirplaneSerializer, \
    CrewSerializer, FlightSerializer, OrderSerializer, RouteListSerializer, RouteDetailSerializer, \
    AirplaneListSerializer, AirplaneDetailSerializer, FlightListSerializer, FlightDetailSerializer, OrderListSerializer, \
    AirportImageSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirportImageSerializer

        return AirportSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        airport = self.get_object()
        serializer = self.get_serializer(airport, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        if source:
            queryset = queryset.filter(source__id=source)

        if destination:
            queryset = queryset.filter(destination__id=destination)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")

        return queryset.distinct()


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer

        return AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("type")

        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_type:
            queryset = queryset.filter(airplane_type__id=airplane_type)

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("airplane_type")

        return queryset.distinct()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer

        return FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("source")
        departure_time = self.request.query_params.get("departure")

        filters = Q()
        if source:
            filters &= Q(route__source__id=source)
        if departure_time:
            time_obj = datetime.strptime(departure_time, "%Y-%m-%d").date()
            filters &= Q(departure_time__date=time_obj)

        if filters:
            queryset = queryset.filter(filters)

        if self.action == "retrieve":
            queryset = queryset.select_related("route", "airplane").prefetch_related("crews")

        if self.action == "list":
            queryset =(
                queryset
                .select_related("route", "airplane")
                .prefetch_related("crews")
                .annotate(
                    tickets_available=(
                        F("airplane__rows") * F("airplane__seats_in_row")
                    ) - Count("tickets")
                )
                .order_by("id")
            )

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = [IsAuthenticated, ]

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        if self.action in ("list", "retrieve"):
            queryset = (
                queryset
                .select_related("user")
                .prefetch_related("tickets__flight")
            )

        order_id = self.request.query_params.get("order")
        if order_id:
            queryset = queryset.filter(id=order_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
