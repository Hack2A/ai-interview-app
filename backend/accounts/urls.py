from django.urls import path
from .views import RegisterView, LoginView, GoogleAuthView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("google/", GoogleAuthView.as_view()),
    path("profile/", ProfileView.as_view()),
]
