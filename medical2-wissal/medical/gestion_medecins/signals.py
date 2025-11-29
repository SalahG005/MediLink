from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Medecin


@receiver(post_save, sender=Medecin)
def notify_admin_new_medecin(sender, instance, created, **kwargs):
    """
    Envoie une notification aux administrateurs lorsqu'un nouveau médecin
    s'inscrit et attend la validation.
    """
    # Vérifier si c'est une nouvelle création et que le statut est en_attente
    if created and instance.statut == 'en_attente':
        # Récupérer tous les administrateurs
        User = get_user_model()
        admins = User.objects.filter(role='admin')
        
        if not admins.exists():
            return  # Pas d'admin, pas de notification
        
        # Importer le modèle Notification
        from rendezvous.models import Notification
        
        # Créer une notification pour chaque administrateur
        nom_medecin = instance.user.get_full_name() or f"{instance.user.first_name} {instance.user.last_name}"
        specialite = instance.specialite.nom_specialite if instance.specialite else "Non spécifiée"
        message = f"Nouveau médecin en attente de validation : {nom_medecin} ({specialite})"
        
        # Vérifier si une notification similaire n'existe pas déjà (éviter les doublons)
        for admin in admins:
            # Vérifier s'il n'y a pas déjà une notification similaire récente (moins de 5 minutes)
            recent_notif = Notification.objects.filter(
                user=admin,
                message__icontains=nom_medecin.split()[0] if nom_medecin.split() else nom_medecin,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()
            
            if not recent_notif:
                Notification.objects.create(
                    user=admin,
                    message=message
                )

