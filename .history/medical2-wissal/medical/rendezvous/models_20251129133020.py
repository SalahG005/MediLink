from django.db import models
from django.conf import settings  # <-- pour utiliser le User personnalisé

# ---- TimeSlot ----
class TimeSlot(models.Model):
    date = models.DateTimeField(unique=True)  # unique = pas de doublons pour le même créneau
    is_available = models.BooleanField(default=True)  # True = disponible, False = réservé

    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M")

# ---- RendezVous ----
class RendezVous(models.Model):
 STATUS_CHOICES = [
    ('pending', 'En attente'),
    ('confirmed', 'Confirmé'),
    ('canceled', 'Annulé'),
    ('rescheduled', 'Reporté'),  # <-- ajouté
]
    # le patient qui a réservé le créneau
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- utiliser le User personnalisé
        on_delete=models.CASCADE
    )

    # un créneau ne peut appartenir qu'à un rendez-vous
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)

    # le statut du rendez-vous
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # motif ou note optionnelle
    motif = models.CharField(max_length=255, blank=True, null=True)

    # date de réservation
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} - {self.slot.date.strftime('%Y-%m-%d %H:%M')} ({self.status})"
