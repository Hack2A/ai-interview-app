from django.urls import path
from .views import CareerActionView, CareerOptionsView

urlpatterns = [
    path('options/', CareerOptionsView.as_view(), name='career-options'),
    path('action/', CareerActionView.as_view(), name='career-action'),
]
