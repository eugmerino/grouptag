from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Custom claims
        token['name'] = user.get_full_name()
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        token['is_admin'] = user.is_admin
        
        # Campos condicionales (evitar error si son null)
        if user.company:
            token['company'] = user.company.name
            token['company_id'] = user.company.id
        if user.dui:
            token['dui'] = user.dui
        if user.position:
            token['position'] = user.position
            
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Datos adicionales en la respuesta
        user = self.user
        data.update({
            'id': user.id,
            'email': user.email,
            'name': user.get_full_name(),
            'is_staff': user.is_staff,
            'is_admin': user.is_admin,
            'company': user.company.name if user.company else None,
            'position': user.position,
            'qr_code': user.qr_code.url if user.qr_code else None
        })
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    company_id = serializers.IntegerField(source='company.id', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'phone', 'dui', 'position', 'company_id',
            'company_name', 'qr_code', 'is_active',
            'is_staff', 'is_admin'
        ]
        read_only_fields = fields  # Todos los campos son solo lectura