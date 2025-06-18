from django.urls import path
from .views import  schedulesMain, attendanceMain

urlpatterns = [
    path('', schedulesMain, name='horarios'),
    path('asistencias/', attendanceMain, name='asistencias'),
]