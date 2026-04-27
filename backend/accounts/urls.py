from django.urls import path
from .views import RegisterView, VerifyRegisterView, LoginView, VerifyLoginView, GoogleAuthView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("verify-register/", VerifyRegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("verify-login/", VerifyLoginView.as_view()),
    path("google/", GoogleAuthView.as_view()),
    path("profile/", ProfileView.as_view()),
]
