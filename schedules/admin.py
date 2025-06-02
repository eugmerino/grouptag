from django.contrib import admin
from .models import Schedule, Attendance
from django.utils.html import format_html


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('user', 'day_of_week_display', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'user')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('user', 'day_of_week')

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()
    day_of_week_display.short_description = 'Día'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user_full_name', 'formatted_date', 'formatted_time', 'attendance_type', 'schedule_info')
    list_filter = ('date', 'type', 'user', 'schedule__day_of_week')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    ordering = ('-date', '-time')
    date_hierarchy = 'date'
    readonly_fields = ('type', 'schedule', 'date', 'time')  # Campos automáticos (no editables)
    fieldsets = (
        (None, {
            'fields': ('user',)  # Solo permitir seleccionar el usuario
        }),
    )

    # Métodos para mejorar la visualización (igual que antes)
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Usuario'

    def formatted_date(self, obj):
        return obj.date.strftime('%d/%m/%Y')
    formatted_date.short_description = 'Fecha'

    def formatted_time(self, obj):
        return obj.time.strftime('%H:%M:%S')
    formatted_time.short_description = 'Hora'

    def attendance_type(self, obj):
        color = 'green' if obj.type == 'check_in' else 'red'
        return format_html('<span style="color: {};">{}</span>', color, obj.get_type_display())
    attendance_type.short_description = 'Tipo'

    def schedule_info(self, obj):
        if obj.schedule:
            return f"{obj.schedule.get_day_of_week_display()} ({obj.schedule.start_time}-{obj.schedule.end_time})"
        return "Sin horario"
    schedule_info.short_description = 'Horario asignado'

    # Sobrescribir el método para guardar en el admin
    def save_model(self, request, obj, form, change):
        # Forzar la lógica automática del modelo al guardar desde el admin
        obj.save()  # Esto ejecutará el método save() del modelo que ya tiene la lógica
