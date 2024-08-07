from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from user.views import UserCreateView, CreateTokenView, ManageUserView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="token"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]

app_name = "user"
