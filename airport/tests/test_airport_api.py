import tempfile
import os
from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route
from airport.serializers import RouteListSerializer, RouteDetailSerializer

AIRPORT_URL = reverse("airport:airport-list")
ROUTE_URL = reverse("airport:route-list")


def sample_airport(**params):
    default = {
        "name": "Sample airport",
        "closest_big_city": "Sample big city",
    }
    default.update(params)

    return Airport.objects.create(**default)


def sample_route(**params):
    default = {
        "source": sample_airport(name="Source airport"),
        "destination": sample_airport(name="Destination airport"),
        "distance": 5000,
    }
    default.update(params)

    return Route.objects.create(**default)


def image_upload_url(airport_id):
    """Return URL for recipe image upload"""
    return reverse("airport:airport-upload-image", args=[airport_id])


def airport_detail_url(airport_id):
    return reverse("airport:airport-detail", args=[airport_id])


def route_detail_url(route_id):
    return reverse("airport:route-detail", args=[route_id])


class RouteUnAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_route_list(self):
        res = self.client.get(ROUTE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_retrieve(self):
        source = sample_airport()
        destination = sample_airport()
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=5000,
        )

        res = self.client.get(route_detail_url(route.id))

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class RouteAuthorizationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@mail.com", "1qazcde3"
        )
        self.client.force_authenticate(self.user)
        self.source = sample_airport(name="Source airport")
        self.destination = sample_airport(name="Destination airport")
        self.route = Route.objects.create(
            source=self.source,
            destination=self.destination,
            distance=5000,
        )

    def test_route_list(self):
        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        ser = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)

    def test_route_retrieve(self):
        res = self.client.get(route_detail_url(self.route.id))
        ser = RouteDetailSerializer(self.route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, ser.data)

    def test_filter_by_source(self):
        route_1 = sample_route(source=sample_airport(name="Source airport 1"))
        route_2 = sample_route(source=sample_airport(name="Source airport 2"))
        res = self.client.get(ROUTE_URL, {"source": route_1.source.name})
        ser_1 = RouteListSerializer(route_1)
        ser_2 = RouteListSerializer(route_2)

        self.assertIn(ser_1.data, res.data)
        self.assertNotIn(ser_2.data, res.data)

    def test_filter_by_destination(self):
        route_1 = sample_route(destination=sample_airport(name="Destination airport 1"))
        route_2 = sample_route(destination=sample_airport(name="Destination airport 2"))
        res = self.client.get(ROUTE_URL, {"destination": route_1.destination.name})
        ser_1 = RouteListSerializer(route_1)
        ser_2 = RouteListSerializer(route_2)

        self.assertIn(ser_1.data, res.data)
        self.assertNotIn(ser_2.data, res.data)


class AirportImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@mail.com", "1qazcde3"
        )
        self.client.force_authenticate(self.user)
        self.airport = sample_airport()
        self.source_airport = sample_airport(name="Source name")
        self.destination_airport = sample_airport(name="Destination name")
        self.route = Route.objects.create(
            source=self.source_airport,
            destination=self.destination_airport,
            distance=5000,
        )

    def tearDown(self):
        self.airport.image.delete()

    def test_upload_image_to_airport(self):
        """Test uploading an image to movie"""
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.airport.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.airport.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.airport.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_airport_list(self):
        url = AIRPORT_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "name": "Name",
                    "closest_big_city": "City",
                    "image": ntf,
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        airport = Airport.objects.get(name="Name")
        self.assertTrue(airport.image)

    def test_image_url_is_shown_on_airport_detail(self):
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(airport_detail_url(self.airport.id))

        self.assertIn("image", res.data)

    def test_image_url_is_shown_on_airport_list(self):
        url = image_upload_url(self.airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(AIRPORT_URL)

        self.assertIn("image", res.data[0].keys())

    def test_image_url_is_shown_on_route_detail(self):
        url = image_upload_url(self.destination_airport.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(route_detail_url(self.route.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("source", res.data)
        self.assertIn("destination", res.data)
        self.assertIn("image", res.data["destination"])
        self.assertIn("image", res.data["destination"].keys())
