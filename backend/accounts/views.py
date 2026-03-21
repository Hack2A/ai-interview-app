import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "message": "User registered successfully",
            "user": UserSerializer(user).data,
            "tokens": get_tokens(user)
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        return Response({
            "user": UserSerializer(user).data,
            "tokens": get_tokens(user)
        }, status=status.HTTP_200_OK)


class GoogleAuthView(APIView):
    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Google token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(google_url, params={"id_token": token})

        if response.status_code != 200:
            return Response(
                {"error": "Invalid Google token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = response.json()

        if data.get("aud") != settings.GOOGLE_CLIENT_ID:
            return Response(
                {"error": "Invalid audience"},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = data.get("email")
        name = data.get("name", "")
        username = email.split("@")[0]

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "username": username,
                "is_onboard": False,
            }
        )

        return Response({
            "user": UserSerializer(user).data,
            "tokens": get_tokens(user),
            "new_user": created
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)