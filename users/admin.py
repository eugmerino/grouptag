from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django import forms
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):  # Heredamos de BaseUserAdmin
    list_display = ('email', 'first_name', 'last_name', 'company', 'phone', 'dui', 'is_active', 'is_admin', 'qr_code_display')
    list_filter = ('company', 'is_active', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name', 'dui', 'phone')
    ordering = ('email',)
    readonly_fields = ('qr_code_display', 'last_login', 'date_joined')
    
    # Campos para edición de usuario existente
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # Password separado para mejor manejo
        ("Información Personal", {
            'fields': ('first_name', 'last_name', 'phone', 'dui', 'company')
        }),
        ("Permisos", {
            'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions')
        }),
        ("Fechas importantes", {
            'fields': ('last_login', 'date_joined')
        }),
        ("Código QR", {
            'fields': ('qr_code_display', 'qr_code')
        }),
    )

    # Campos para creación de nuevo usuario
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name'),
        }),
        ("Información Adicional", {
            'fields': ('phone', 'dui', 'company')
        }),
    )

    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html(f'<img src="{obj.qr_code.url}" width="100" height="100" />')
        return "Sin QR"
    qr_code_display.short_description = "Código QR"

    # Validación adicional para contraseñas
    def save_model(self, request, obj, form, change):
        if not change and 'password1' in form.cleaned_data:
            # Para nuevos usuarios
            obj.set_password(form.cleaned_data['password1'])
        elif 'password' in form.cleaned_data and form.cleaned_data['password']:
            # Si se cambia la contraseña en un usuario existente
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)
