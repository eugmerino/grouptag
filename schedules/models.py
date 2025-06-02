from django.db import models
from users.models import User
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
    is_late = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('user', 'date', 'type')
        ordering = ['-date', '-time']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.date} {self.time} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        # Determinar si es tarde comparando con el horario programado
        if not self.pk and self.type == 'check_in':
            today_weekday = self.date.weekday()
            try:
                schedule = Schedule.objects.get(
                    user=self.user, 
                    day_of_week=today_weekday,
                    is_active=True
                )
                self.schedule = schedule
                if self.time > schedule.start_time:
                    self.is_late = True
            except Schedule.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)