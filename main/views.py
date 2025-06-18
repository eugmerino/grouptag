from django.shortcuts import render, redirect
from .form import UserRegistrationForm
from django.contrib.auth import login,logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from companies.models import Company
from users.models import User

# Create your views here.
def startPage(request):
    return render(request, 'startpage.html')

def aboutPage(request):
    return render(request, 'about.html')

def subscriptionPage(request):
    return render(request, 'subscription.html')

def loginPage(request):
    message = ''
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            if user.is_admin:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.warning(request, 'No tienes acceso al panel de administración.')
        else:
            messages.warning(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    objects = {
        "form": UserRegistrationForm(),
        "message": message
    }
    return render(request, 'login.html', objects)

@login_required(login_url='login')
def logoutPage(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Has cerrado sesión correctamente.')
        return redirect('logingrouptag')
    return render(request, 'logout.html')

@login_required(login_url='login')
def dashboardPage(request):
    user = request.user
    users = User.objects.filter(company=user.company).exclude(id=user.id)
    objects = {
        "usuario": user,
        "usuarios": users
    }
    return render(request, 'dashboard.html', objects)