from django.apps import AppConfig


class GestionMedecinsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion_medecins'
    
    def ready(self):
        import gestion_medecins.signals  # Enregistrer les signaux