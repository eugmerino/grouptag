from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from companies.models import Company
import qrcode
from io import BytesIO
from django.core.files import File
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        if not password:
            raise ValueError('La contraseña es obligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        
        # Valores por defecto para superuser
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')
        extra_fields.setdefault('dui', '00000000-0')  # DUI genérico para admin
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Representa a los usuarios del sistema (empleados)
    """
    company = models.ForeignKey(
        Company,
        related_name='employees',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    phone = models.CharField(
        "Teléfono",
        max_length=20,
        null=True,
        blank=True,
        unique=True
    )

    dui = models.CharField(
        "Dui",
        max_length=10,
        null=True,
        blank=True,
        unique=True
    )

    qr_code = models.ImageField(
        "QR",
        upload_to='qr_codes/',
        null=True,
        blank=True
    )

    position = models.CharField(
        "Puesto",
        max_length=100,
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        "Estado",
        default=True
    )
    is_admin = models.BooleanField(
        "Admin",
        default=False
    )
    
    username = None
    email = models.EmailField(
        "Correo",
        unique=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Ahora vacío para superuser
    
    objects = UserManager()  # Usamos el manager personalizado
    
    def __str__(self):
        company_name = self.company.name if self.company else "Sin compañía"
        return f"{self.get_full_name()} ({company_name})"
    
    def save(self, *args, **kwargs):
        # Generar QR code basado en DUI al crear/actualizar usuario
        if not self.qr_code and self.dui:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            company_id = self.company.id if self.company else 0
            qr_data = f"EMP-{company_id}-{self.dui}-{uuid.uuid4().hex[:6]}"
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            file_name = f'qr_{self.dui}_{uuid.uuid4().hex[:8]}.png'
            
            self.qr_code.save(file_name, File(buffer), save=False)
        
        super().save(*args, **kwargs)