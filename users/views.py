from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from django.shortcuts import render,redirect
from django.views import View
from .models import User
from django.contrib.auth.decorators import login_required
from .forms import AdminUserCreationForm

class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

@login_required(login_url='login') 
def userMain(request):
    user = request.user
    empleados = User.objects.filter(company=user.company).exclude(id=user.id)

    
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_empleado = form.save(commit=False)
            nuevo_empleado.company = user.company  # Forzar que pertenezca a la misma empresa
            nuevo_empleado.save()
            
            return redirect('usuarios')
    else:
        form = AdminUserCreationForm()
    context = {
            "empleados": empleados,
            "form": form,
            "usuario": user,  # Para mantener coherencia si usas {{ usuario }}
        }
        
    return render(request, 'usermain.html', context)