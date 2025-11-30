from django.db import models
from django.conf import settings  # <-- pour utiliser le User personnalisé

# ---- TimeSlot ----
class TimeSlot(models.Model):
    medecin = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,
    limit_choices_to={'role': 'medecin'}
)

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
        ('rescheduled', 'Reporté'),
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
        # user model may not have username (custom User). Prefer full name then email.
        patient_name = getattr(self.patient, 'get_full_name', None)
        if callable(patient_name):
            name = self.patient.get_full_name() or getattr(self.patient, 'email', str(self.patient))
        else:
            name = getattr(self.patient, 'email', str(self.patient))
        return f"{name} - {self.slot.date.strftime('%Y-%m-%d %H:%M')} ({self.status})"

        
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        user_name = getattr(self.user, 'get_full_name', None)
        if callable(user_name):
            display = self.user.get_full_name() or getattr(self.user, 'email', str(self.user))
        else:
            display = getattr(self.user, 'email', str(self.user))
        return f"Notif pour {display} — {self.message[:20]}..."
