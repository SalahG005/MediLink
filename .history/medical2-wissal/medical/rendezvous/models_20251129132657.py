from django.db import models
from django.conf import settings  # <-- pour utiliser le User personnalisé

# ---- TimeSlot ----
class TimeSlot(models.Model):
    date = models.DateTimeField(unique=True)  # unique = pas de doublons pour le même créneau
    is_available = models.BooleanField(default=True)  # True = disponible, False = réservé

    def __str__(self):
        return self.date.strftime("%Y-%m-%d %H:%M")

# ---- RendezVous ----
# models.py
class RendezVous(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmé'),
        ('canceled', 'Annulé'),
        ('rescheduled', 'Reporté'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slot = models.OneToOneField(TimeSlot, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    motif = models.CharField(max_length=255, blank=True, null=True)

    # commentaire du médecin
    doctor_note = models.TextField(blank=True, null=True)

    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.username} – {self.slot.date} ({self.status})"
