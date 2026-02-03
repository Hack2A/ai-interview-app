from rest_framework import serializers
from .models import UserOnboarding

class OnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserOnboarding
        fields = [
            'institution', 
            'profession', 
            'experience', 
            'resume', 
            'gender', 
            'phone_number', 
            'graduation_year',
        ]
        
    def create(self, validated_data):
        user = self.context['request'].user
        onboarding = UserOnboarding.objects.create(user=user, **validated_data)
        
        # Update user status
        user.is_onboard = True
        user.save()
        
        return onboarding
