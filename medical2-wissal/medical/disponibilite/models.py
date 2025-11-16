from django.db import models
from users.models import User  # ton modèle utilisateur personnalisé

class Disponibilite(models.Model):
    medecin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'medecin'},  # permet de ne choisir que les médecins
        related_name='disponibilites',
        verbose_name="Médecin"
    )
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medecin.get_full_name()} - {self.date} ({self.heure_debut}-{self.heure_fin})"
