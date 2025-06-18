from django.db import models
from users.models import User
from django.utils import timezone
from django.utils.timezone import localtime
import datetime

class Schedule(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField("Día", choices=DAYS_OF_WEEK)
    start_time = models.TimeField("Hora de llegada")
    end_time = models.TimeField("Hora de salida")
    
    class Meta:
        unique_together = ('user', 'day_of_week')
        ordering = ['user', 'day_of_week']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_day_of_week_display()}: {self.start_time} a {self.end_time}"


class Attendance(models.Model):
    ATTENDANCE_TYPES = (
        ('check_in', 'Entrada'),
        ('check_out', 'Salida'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=datetime.date.today)
    time = models.TimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=ATTENDANCE_TYPES)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'date', 'type')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date} {self.time} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        # Obtener la fecha y hora actual
        now = localtime()
        self.date = now.date()
        
        # Obtener el día de la semana (0=Lunes, 6=Domingo)
        day_of_week = now.weekday()
        
        # Buscar el horario correspondiente al usuario y día de la semana
        try:
            self.schedule = Schedule.objects.get(user=self.user, day_of_week=day_of_week)
        except Schedule.DoesNotExist:
            self.schedule = None
        
        # Verificar registros existentes para el usuario en la fecha actual
        existing_attendances = Attendance.objects.filter(
            user=self.user, 
            date=self.date
        ).order_by('time')
        
        # Determinar el tipo de registro
        if existing_attendances.count() == 0:
            # Primer registro del día: Entrada
            self.type = 'check_in'
        else:
            # Segundo o posterior registro: Salida
            self.type = 'check_out'
            
            # Si ya existe una salida, eliminarla antes de guardar la nueva
            existing_checkouts = existing_attendances.filter(type='check_out')
            if existing_checkouts.exists():
                existing_checkouts.delete()
        
        super().save(*args, **kwargs)