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
import random
from django.core.cache import cache
from django.core.mail import send_mail

def get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

def generate_otp():
    return str(random.randint(100000, 999999))

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp = generate_otp()
        
        cache_key = f"register_{email}"
        cache.set(cache_key, {
            "otp": otp,
            "user_data": request.data
        }, timeout=300)
        
        send_mail(
            "Your Registration OTP",
            f"Your OTP code is {otp}. It is valid for 5 minutes.",
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ai-interview-app.com'),
            [email],
            fail_silently=False,
        )

        return Response({
            "message": "OTP sent to email. Please verify."
        }, status=status.HTTP_200_OK)

class VerifyRegisterView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"register_{email}"
        cached_data = cache.get(cache_key)
        
        if not cached_data or str(cached_data.get("otp")) != str(otp):
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = RegisterSerializer(data=cached_data.get("user_data"))
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        cache.delete(cache_key)
        
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

        email = user.email
        otp = generate_otp()
        
        cache_key = f"login_{email}"
        cache.set(cache_key, otp, timeout=300)
        
        send_mail(
            "Your Login OTP",
            f"Your OTP code is {otp}. It is valid for 5 minutes.",
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@ai-interview-app.com'),
            [email],
            fail_silently=False,
        )

        return Response({
            "message": "OTP sent to email. Please verify."
        }, status=status.HTTP_200_OK)

class VerifyLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        
        if not email or not otp:
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_key = f"login_{email}"
        cached_otp = cache.get(cache_key)
        
        if not cached_otp or str(cached_otp) != str(otp):
            return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        cache.delete(cache_key)
        
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