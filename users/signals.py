from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def sync_profiles_with_user(sender, instance, created, **kwargs):
    """
    Crée ou met à jour automatiquement les profils Patient et Médecin
    en fonction du rôle choisi lors de l'inscription.
    """
    from dossiers.models import Patient
    from gestion_medecins.models import Medecin

    role = getattr(instance, 'role', None)

    if role == 'patient':
        defaults = {
            'nom': instance.last_name,
            'prenom': instance.first_name,
            'date_naissance': getattr(instance, 'date_of_birth', None),
            'telephone': getattr(instance, 'phone', ''),
        }
        Patient.objects.update_or_create(user=instance, defaults=defaults)

    elif role == 'medecin':
        defaults = {
            'specialite': getattr(instance, 'specialite', ''),
            'telephone': getattr(instance, 'phone', ''),
        }
        Medecin.objects.update_or_create(user=instance, defaults=defaults)

