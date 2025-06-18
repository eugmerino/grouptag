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
