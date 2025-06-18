from django import forms
from .models import Schedule



class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['user', 'day_of_week', 'start_time', 'end_time']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'day_of_week': forms.Select(attrs={'class': 'form-control form-control-lg'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-lg'}),
        }
        labels = {
            'user': 'Empleado',
            'day_of_week': 'Día de la semana',
            'start_time': 'Hora de llegada',
            'end_time': 'Hora de salida',
        }
