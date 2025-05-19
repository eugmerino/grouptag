from django.db import models

class Company(models.Model):
    """
        Representa una empresa (Organización)
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Organización"
        verbose_name_plural = "Organizaciones"
        constraints = [
            models.UniqueConstraint(
                fields=['name'], 
                name='unique_company_name'
            )
        ]