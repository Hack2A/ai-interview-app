from django.urls import re_path
from .views import CareerActionView, CareerOptionsView

urlpatterns = [
    re_path(r'^options/?$', CareerOptionsView.as_view(), name='career-options'),
    re_path(r'^action/?$', CareerActionView.as_view(), name='career-action'),
]
