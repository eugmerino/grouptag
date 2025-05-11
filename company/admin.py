from django.contrib import admin
from .models import Company

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ('name', 'truncated_description')
    search_fields = ['name']
    list_per_page = 20
    
    def truncated_description(self, obj):
        return f"{obj.description[:50]}..." if obj.description else ""
    truncated_description.short_description = "Descripción (resumen)"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].label = "Nombre*"  # Asterisco para obligatorio
        form.base_fields['description'].label = "Descripción*"
        return form