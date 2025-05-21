from django.contrib import admin
from .models import Schedule, Attendance

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'day_of_week_display', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('user', 'day_of_week')

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'Día'

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'time', 'type_display', 'schedule', 'is_late')
    list_filter = ('type', 'is_late', 'date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-date', '-time')

    def type_display(self, obj):
        return obj.get_type_display()
    type_display.short_description = 'Tipo de Registro'
