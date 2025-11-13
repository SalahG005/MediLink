from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

# ✅ 1. Vérifie que le nom contient uniquement des lettres et des espaces
name_validator = RegexValidator(
    r'^[a-zA-ZÀ-ÿ\s]+$',
    message="Le nom ne doit contenir que des lettres et des espaces."
)

class Specialite(models.Model):
    id_specialite = models.AutoField(primary_key=True)

    # ✅ 2. Nom obligatoire, unique, min 3 caractères
    nom_specialite = models.CharField(
        "Nom de la spécialité",
        max_length=100,
        unique=True,  # 🚫 empêche les doublons
        validators=[
            name_validator,  # 🚫 empêche chiffres et caractères spéciaux
            MinLengthValidator(3, "Le nom doit comporter au moins 3 caractères.")
        ]
    )

    # ✅ 3. Description optionnelle mais min 10 caractères si remplie
    description = models.TextField(
        "Description",
        validators=[
            MinLengthValidator(10, "La description doit comporter au moins 10 caractères.")
        ],
        blank=True,  # ⚙️ champ facultatif dans les formulaires
        null=True    # ⚙️ champ facultatif dans la base de données
    )

    # ✅ 4. Validation logique personnalisée
    def clean(self):
        if self.nom_specialite.lower() == "test":
            raise ValidationError("Le nom 'test' n'est pas autorisé.")

    def __str__(self):
        return self.nom_specialite
