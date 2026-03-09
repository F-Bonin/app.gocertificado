from django.urls import path
from .views import UserRegistrationView, CustomLoginView, CustomLogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("register/", UserRegistrationView.as_view(), name="register"),
]
