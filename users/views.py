from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserProfileSerializer
from django.shortcuts import render
from django.views import View

class RegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)