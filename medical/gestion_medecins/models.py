from django.conf import settings
from django.db import models


class Medecin(models.Model):
    """Modèle pour gérer les médecins et leur statut d'inscription"""
    
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('valide', 'Validé'),
        ('refuse', 'Refusé'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medecin_profile'
    )
    numero_ordre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro d'ordre",
        null=True,
        blank=True
    )
    specialite = models.CharField(max_length=100, verbose_name="Spécialité", blank=True)
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente', verbose_name="Statut")
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="Date de validation")

    class Meta:
        verbose_name = "Médecin"
        verbose_name_plural = "Médecins"
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.specialite} ({self.get_statut_display()})"
