from rest_framework import routers
from django.urls import path, include

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneViewSet,
    FlightViewSet,
    OrderViewSet,
    AirplaneTypeViewSet,
    CrewViewSet,
)

router = routers.DefaultRouter()
router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("crews", CrewViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
