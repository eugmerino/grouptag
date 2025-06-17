# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_attendance(request):
    dui = request.data.get('dui')
    registrar_user = request.user  # Usuario que registra (sesión actual)
    
    try:
        # Buscar al usuario por DUI
        employee = User.objects.get(dui=dui)
        
        # Verificar si pertenecen a la misma compañía
        if employee.company != registrar_user.company:
            return Response(
                {"error": "El empleado no pertenece a tu compañía"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear registro de asistencia
        attendance = Attendance(
            user=employee,
            type='check_in'  # O determinar check_in/check_out como en tu save()
        )
        attendance.save()
        
        return Response({
            "success": True,
            "message": f"Asistencia registrada: {employee.get_full_name()}",
            "type": attendance.get_type_display(),
            "time": attendance.time.strftime("%H:%M:%S")
        })
        
    except User.DoesNotExist:
        return Response(
            {"error": "No se encontró empleado con este DUI"},
            status=status.HTTP_404_NOT_FOUND
        )