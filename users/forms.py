from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Asegúrate de importar tu modelo personalizado


class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'position',
            'phone',
            'dui',
            'is_active',
            'is_admin',
        ]
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-lg'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Estilo Bootstrap
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control form-control-lg'

        # Cambiar etiquetas (labels)
        self.fields['first_name'].label = 'Nombres'
        self.fields['last_name'].label = 'Apellidos'
        self.fields['dui'].label = 'DUI'
        self.fields['phone'].label = 'Teléfono'
        self.fields['position'].label = 'Puesto'
        self.fields['is_active'].label = '¿Activo?'
        self.fields['is_admin'].label = '¿Administrador?'
