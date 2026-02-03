from django.db import models
from accounts.models import User

class UserOnboarding(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="onboarding")
    institution = models.CharField(max_length=255)
    profession = models.CharField(max_length=100)
    experience = models.CharField(max_length=100)
    resume = models.FileField(upload_to='resumes/')
    gender = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    graduation_year = models.IntegerField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Onboarding"
