from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import UserOnboarding
from .serializers import OnboardingSerializer

class OnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            onboarding = UserOnboarding.objects.get(user=request.user)
            serializer = OnboardingSerializer(onboarding)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserOnboarding.DoesNotExist:
            return Response(
                {"error": "Onboarding details not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    def post(self, request):
        # Check if already onboarded
        if hasattr(request.user, 'onboarding'):
             return Response(
                {"error": "User already onboarded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OnboardingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        try:
            onboarding = UserOnboarding.objects.get(user=request.user)
        except UserOnboarding.DoesNotExist:
            return Response(
                {"error": "Onboarding details not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OnboardingSerializer(
            onboarding, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
