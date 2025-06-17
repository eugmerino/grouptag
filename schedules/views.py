from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime

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