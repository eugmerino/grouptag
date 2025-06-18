from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.utils.timezone import localtime
from datetime import datetime, date, time
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Schedule, Attendance
from django.db.models import Prefetch




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
        now = localtime()
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








def calculate_punctuality(entry, schedule):
    if not schedule or not hasattr(schedule, 'start_time'):
        return "Sin horario"
    if not entry:
        return "Sin marcaje"
    
    # Convertimos los time a datetime para poder restarlos
    today = date.today()
    entry_datetime = datetime.combine(today, entry.time)
    scheduled_datetime = datetime.combine(today, schedule.start_time)
    
    if entry_datetime <= scheduled_datetime:
        return "A tiempo"
    else:
        delay = entry_datetime - scheduled_datetime
        delay_minutes = delay.total_seconds() // 60
        return f"Tarde: {int(delay_minutes)} min"

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def employee_attendance_report(request):
    # Si el usuario no es admin, solo mostramos su información
    if not request.user.is_admin:
        return get_single_user_report(request)
    
    # El resto del código sigue igual para usuarios admin
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
    
    # Optimización de consultas con Prefetch
    attendance_prefetch = Prefetch(
        'attendances',
        queryset=Attendance.objects.filter(date=target_date).order_by('time'),
        to_attr='daily_attendances'
    )
    
    employees = User.objects.filter(
        company=company,
        is_active=True
    ).prefetch_related(
        attendance_prefetch,
        'schedules'
    )
    
    report_data = []
    for employee in employees:
        # Accedemos a las asistencias ya prefiltradas
        daily_attendances = employee.daily_attendances
        entry = next((a for a in daily_attendances if a.type == 'check_in'), None)
        exit_ = next((a for a in daily_attendances if a.type == 'check_out'), None)
        
        # Buscamos el horario para el día de la semana
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
    
    return Response({
        'date': target_date.strftime("%Y-%m-%d"),
        'employees': report_data
    })

def get_single_user_report(request):
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
    
    # Obtenemos solo el usuario actual
    employee = request.user
    
    # Obtenemos las asistencias del usuario para la fecha
    daily_attendances = Attendance.objects.filter(
        user=employee,
        date=target_date
    ).order_by('time')
    
    entry = next((a for a in daily_attendances if a.type == 'check_in'), None)
    exit_ = next((a for a in daily_attendances if a.type == 'check_out'), None)
    
    # Buscamos el horario para el día de la semana
    try:
        schedule = Schedule.objects.get(
            user=employee,
            day_of_week=target_date.weekday()
        )
    except Schedule.DoesNotExist:
        schedule = None
    
    report_data = {
        'id': employee.id,
        'full_name': employee.get_full_name(),
        'entry_time': entry.time.strftime("%H:%M:%S") if entry else "-",
        'exit_time': exit_.time.strftime("%H:%M:%S") if exit_ else "-",
        'punctuality': calculate_punctuality(entry, schedule),
        'has_both_entries': entry and exit_ is not None
    }
    
    return Response({
        'date': target_date.strftime("%Y-%m-%d"),
        'employees': [report_data]  # Mantenemos la misma estructura pero con un solo usuario
    })



# schedules/views.py
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_schedule(request):
    schedules = Schedule.objects.filter(user=request.user).order_by('day_of_week')
    
    response_data = []
    for day in range(7):  # 0=Lunes, 6=Domingo
        schedule = next((s for s in schedules if s.day_of_week == day), None)
        response_data.append({
            'day': day,
            'day_name': Schedule.DAYS_OF_WEEK[day][1],
            'start_time': schedule.start_time.strftime('%H:%M') if schedule else None,
            'end_time': schedule.end_time.strftime('%H:%M') if schedule else None
        })
    
    return Response(response_data)
from django.shortcuts import render,redirect
from .models import Schedule, Attendance
from users.models import User
from django.contrib.auth.decorators import login_required
from .forms import ScheduleForm


# Create your views here.
@login_required(login_url='login')
def schedulesMain(request):
    user = request.user
    usuarios = User.objects.filter(company=user.company)
    horarios = Schedule.objects.filter(user__company=user.company).order_by('day_of_week')

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            # Verificamos que el usuario pertenezca a la misma empresa
            if schedule.user.company == user.company:
                schedule.save()
                return redirect('horarios')  # Asegúrate que esta sea la URL name correspondiente
    else:
        form = ScheduleForm()

    context = {
        'horarios': horarios,
        'usuarios': usuarios,
        'form': form,
    }
    return render(request, 'schedulesmain.html', context)

@login_required(login_url='login')
def attendanceMain(request):
    user = request.user
    
    empleados = User.objects.filter(company=user.company)
    asistencias = Attendance.objects.filter(user__company=user.company) # Reset attendance status
    horarios = Schedule.objects.filter(user__company=user.company).order_by('day_of_week')
    objects = {
        'empleados': empleados,
        'asistencias': asistencias,
        'horarios': horarios
    }

    return render(request, 'attendancemain.html', objects)
