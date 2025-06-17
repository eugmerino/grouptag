from django.urls import path
from .views import register_attendance

urlpatterns = [
    path('attendance/', register_attendance, name='register-attendance'),
    path('attendance-report/', employee_attendance_report, name='attendance-report'),
]