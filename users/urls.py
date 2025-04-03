from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    UserListCreateView,
    UserDetailView,
    UserActivationView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", UserListCreateView.as_view(), name="user-list-create"),
    path("<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    path(
        "<int:user_id>/activation/",
        UserActivationView.as_view(),
        name="user-activation",
    ),
]
