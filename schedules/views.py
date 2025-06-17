from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Schedule, Attendance



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_attendance(request):
    dui = request.data.get('dui')
    registrar_user = request.user
    
    try:
        # 1. Buscar al usuario por DUI
        employee = User.objects.get(dui=dui)
        
        # 2. Verificar misma compañía
        if employee.company != registrar_user.company:
            return Response(
                {"error": "El empleado no pertenece a tu compañía"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 3. Obtener día actual (0=Lunes, 6=Domingo)
        now = timezone.now()
        day_of_week = now.weekday()  # Devuelve 0 para Lunes, 1 para Martes, etc.
        
        # 4. Verificar si tiene horario para hoy
        try:
            schedule = Schedule.objects.get(
                user=employee,
                day_of_week=day_of_week
            )
        except Schedule.DoesNotExist:
            return Response(
                {
                    "error": f"El empleado no tiene horario programado para {now.strftime('%A')}",
                    "day": day_of_week,
                    "day_name": now.strftime('%A')  # Nombre del día (ej: "Monday")
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 5. Determinar tipo de registro (check_in/check_out)
        existing = Attendance.objects.filter(
            user=employee,
            date=now.date()
        ).order_by('time')
        
        if existing.count() == 0:
            record_type = 'check_in'
        else:
            record_type = 'check_out'
            # Eliminar check_out existente si hay más de uno
            existing.filter(type='check_out').delete()
        
        # 6. Crear registro
        attendance = Attendance(
            user=employee,
            type=record_type,
            schedule=schedule  # Asignar el horario encontrado
        )
        attendance.save()
        
        return Response({
            "success": True,
            "message": f"Asistencia {attendance.get_type_display()} registrada",
            "employee": employee.get_full_name(),
            "time": attendance.time.strftime("%H:%M:%S"),
            "schedule": {
                "day": schedule.get_day_of_week_display(),
                "start_time": schedule.start_time.strftime("%H:%M"),
                "end_time": schedule.end_time.strftime("%H:%M")
            }
        })
        
    except User.DoesNotExist:
        return Response(
            {"error": "No se encontró empleado con este DUI"},
            status=status.HTTP_404_NOT_FOUND
        )



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_attendance_report(request):
    company = request.user.company
    
    # Manejo seguro de la fecha
    date_str = request.query_params.get('date')
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD."},
                status=400
            )
    else:
        target_date = timezone.now().date()
    
    # Optimización: Prefetch relacionado y filtrado en DB
    employees = User.objects.filter(
        company=company,
        is_active=True
    ).prefetch_related(
        'attendance_set',
        'schedules'
    )
    
    report_data = []
    for employee in employees:
        # Obtener asistencias del día en una sola consulta
        attendances = employee.attendance_set.filter(date=target_date).order_by('time')
        entry = next((a for a in attendances if a.type == 'check_in'), None)
        exit_ = next((a for a in attendances if a.type == 'check_out'), None)
        
        # Obtener horario para el día de la semana (0=lunes, 6=domingo)
        schedule = next(
            (s for s in employee.schedules.all() if s.day_of_week == target_date.weekday()),
            None
        )
        
        report_data.append({
            'id': employee.id,
            'full_name': employee.get_full_name(),
            'entry_time': entry.time.strftime("%H:%M:%S") if entry else "-",
            'exit_time': exit_.time.strftime("%H:%M:%S") if exit_ else "-",
            'punctuality': calculate_punctuality(entry, schedule),
            'has_both_entries': entry and exit_ is not None
        })
    
    return Response({'date': target_date.strftime("%Y-%m-%d"), 'employees': report_data})

def calculate_punctuality(entry, schedule):
    if not entry or not schedule:
        return "Sin horario"
    
    entry_time = entry.time
    scheduled_time = schedule.start_time
    
    if entry_time <= scheduled_time:
        return "A tiempo"
    else:
        delay = entry_time - scheduled_time
        return f"Tardanza: {delay.seconds // 60} min"