from django.db import models

class Company(models.Model):
    """
    Representa la información de la Compañía
    """
    name = models.CharField(
        "Nombre", 
        max_length=200,
        blank=False,
        null=False,
        help_text="Nombre completo de la organización"
    )
    
    description = models.TextField(
        "Descripción",
        blank=False,
        null=False,
        help_text="Descripción detallada de la organización"
    )

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        constraints = [
            models.UniqueConstraint(
                fields=['name'], 
                name='unique_company_name'
            )
        ]

    def __str__(self):
        return self.name