from django.contrib import admin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'company', 'phone', 'dui', 'is_active', 'is_admin', 'qr_code_display')
    list_filter = ('company', 'is_active', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name', 'dui', 'phone')
    ordering = ('email',)
    readonly_fields = ('qr_code_display',)

    fieldsets = (
        ("Información Personal", {
            'fields': ('email', 'password', 'first_name', 'last_name', 'phone', 'dui', 'company')
        }),
        ("Permisos", {
            'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser')
        }),
        ("Código QR", {
            'fields': ('qr_code_display',)
        }),
    )

    def qr_code_display(self, obj):
        if obj.qr_code:
            return format_html(f'<img src="{obj.qr_code.url}" width="100" height="100" />')
        return "Sin QR"

    qr_code_display.short_description = "Código QR"

    def save_model(self, request, obj, form, change):
        # Si es un nuevo usuario o se está cambiando la contraseña
        if not change or 'password' in form.changed_data:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)