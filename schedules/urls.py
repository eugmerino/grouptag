from django.urls import path
from .views import  schedulesMain, attendanceMain
from .views import register_attendance, employee_attendance_report, weekly_schedule

urlpatterns = [
    path('', schedulesMain, name='horarios'),
    path('asistencias/', attendanceMain, name='asistencias'),
    path('attendance/', register_attendance, name='register-attendance'),
    path('attendance-report/', employee_attendance_report, name='attendance-report'),
    path('weekly-schedule/', weekly_schedule, name='weekly-schedule'),
]