from django.urls import path
from .views import UserProfileView

urlpatterns = [
    path('api/attendance/', register_attendance, name='register-attendance'),
]