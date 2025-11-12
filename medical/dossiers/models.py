from django.conf import settings
from django.db import models


class Patient(models.Model):
    """Modèle pour les patients"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name="Utilisateur"
    )
    nom = models.CharField(max_length=100, verbose_name="Nom", blank=True)
    prenom = models.CharField(max_length=100, verbose_name="Prénom", blank=True)
    date_naissance = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    sexe = models.CharField(
        max_length=1,
        choices=[('M', 'Masculin'), ('F', 'Féminin')],
        verbose_name="Sexe",
        blank=True
    )
    telephone = models.CharField(max_length=20, verbose_name="Téléphone", blank=True)
    adresse = models.TextField(verbose_name="Adresse", blank=True)
    numero_carte_identite = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de carte d'identité",
        null=True,
        blank=True
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.email}"


class DossierMedical(models.Model):
    """Modèle pour les dossiers médicaux"""

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='dossiers', verbose_name="Patient")
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='dossiers_crees',
        verbose_name="Médecin"
    )
    date_consultation = models.DateTimeField(auto_now_add=True, verbose_name="Date de consultation")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")

    # Informations médicales
    motif_consultation = models.TextField(verbose_name="Motif de consultation")
    diagnostic = models.TextField(verbose_name="Diagnostic")
    traitement = models.TextField(verbose_name="Traitement prescrit")
    observations = models.TextField(blank=True, verbose_name="Observations")
    allergies = models.TextField(blank=True, verbose_name="Allergies connues")
    antecedents = models.TextField(blank=True, verbose_name="Antécédents médicaux")
    
    class Meta:
        verbose_name = "Dossier médical"
        verbose_name_plural = "Dossiers médicaux"
        ordering = ['-date_consultation']
    
    def __str__(self):
        return f"Dossier de {self.patient} - {self.date_consultation.strftime('%d/%m/%Y')}"
