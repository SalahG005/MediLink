# users/models.py
from datetime import date
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator, EmailValidator, FileExtensionValidator

# Validators
name_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÿ\s]+$',
    message="Ce champ doit contenir uniquement des lettres et des espaces."
)
phone_validator = RegexValidator(
    regex=r'^\d{8}$',
    message="Le numéro de téléphone doit contenir exactement 8 chiffres."
)
postal_code_validator = RegexValidator(
    regex=r'^\d{4}$',
    message="Le code postal doit contenir exactement 4 chiffres."
)
year_validator = RegexValidator(
    regex=r'^\d{4}$',
    message="L’année doit contenir exactement 4 chiffres."
)
city_validator = RegexValidator(
    regex=r'^[A-Za-zÀ-ÿ\s]+$',
    message="La ville doit contenir uniquement des lettres et des espaces."
)

GOUVERNORATS = [
    ('Tunis', 'Tunis'), ('Ariana', 'Ariana'), ('Ben Arous', 'Ben Arous'), ('Mannouba', 'Mannouba'),
    ('Bizerte', 'Bizerte'), ('Nabeul', 'Nabeul'), ('Béja', 'Béja'), ('Jendouba', 'Jendouba'),
    ('Zaghouan', 'Zaghouan'), ('Siliana', 'Siliana'), ('Le Kef', 'Le Kef'), ('Sousse', 'Sousse'),
    ('Monastir', 'Monastir'), ('Mahdia', 'Mahdia'), ('Kasserine', 'Kasserine'),
    ('Sidi Bouzid', 'Sidi Bouzid'), ('Kairouan', 'Kairouan'), ('Gafsa', 'Gafsa'),
    ('Sfax', 'Sfax'), ('Gabès', 'Gabès'), ('Médenine', 'Médenine'),
    ('Tozeur', 'Tozeur'), ('Kebili', 'Kebili'), ('Tataouine', 'Tataouine'),
]

SPECIALITES = [
    ('cardiologie', 'Cardiologie'),
    ('dermatologie', 'Dermatologie'),
    ('endocrinologie', 'Endocrinologie'),
    ('gastro-entérologie', 'Gastro-entérologie'),
    ('génétique médicale', 'Génétique médicale'),
    ('gériatrie', 'Gériatrie'),
    ('hématologie', 'Hématologie'),
    ('immunologie clinique et allergie', 'Immunologie clinique et allergie'),
    ('médecine interne', 'Médecine interne'),
    ("médecine d'urgence", "Médecine d'urgence"),
    ('néphrologie', 'Néphrologie'),
    ('neurologie', 'Neurologie'),
    ('oncologie médicale', 'Oncologie médicale'),
    ('pédiatrie', 'Pédiatrie'),
    ('physiatrie', 'Physiatrie'),
    ('pneumologie', 'Pneumologie'),
    ('psychiatrie', 'Psychiatrie'),
    ('rhumatologie', 'Rhumatologie'),
]

STATUT_CHOICES = [
    ('en cours', 'En cours'),
    ('verifie', 'Vérifié'),
    ('exclu', 'Exclu'),
]

ROLE_CHOICES = [
    ('patient', 'Patient'),
    ('medecin', 'Médecin'),
    ('admin', 'Administrateur'),
]

# -------------------------
# MANAGER PERSONNALISÉ
# -------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('first_name', extra_fields.get('first_name', 'Admin'))
        extra_fields.setdefault('last_name', extra_fields.get('last_name', 'User'))
        extra_fields.setdefault('phone', extra_fields.get('phone', '00000000'))
        extra_fields.setdefault('date_of_birth', extra_fields.get('date_of_birth', date(2000, 1, 1)))
        extra_fields.setdefault('gouvernorat', extra_fields.get('gouvernorat', GOUVERNORATS[0][0]))
        extra_fields.setdefault('ville', extra_fields.get('ville', GOUVERNORATS[0][0]))

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# -------------------------
# MODELE USER UNIQUE
# -------------------------
class User(AbstractUser):
    username = None  # On supprime le champ username
    email = models.EmailField(unique=True, validators=[EmailValidator(message="Email invalide")])
    first_name = models.CharField("Prénom", max_length=50, validators=[name_validator])
    last_name = models.CharField("Nom", max_length=50, validators=[name_validator])
    phone = models.CharField("Téléphone", max_length=8, validators=[phone_validator])
    date_of_birth = models.DateField("Date de naissance")
    gouvernorat = models.CharField("Gouvernorat", max_length=50, choices=GOUVERNORATS)
    ville = models.CharField("Ville", max_length=50, validators=[city_validator])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    #champs specifiques aux patients
    etat_compte = models.CharField(
        max_length=20,
        choices=[('actif', 'Actif'), ('archive', 'Archivé')],
        default='actif'
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def archiver_compte(self):
        self.etat_compte = 'archive'
        self.save()

    def supprimer_compte(self):
        self.delete()

    # Champs spécifiques aux médecins
    code_postal = models.CharField("Code postal", max_length=4, validators=[postal_code_validator], null=True, blank=True)
    specialite = models.CharField("Spécialité", max_length=100, choices=SPECIALITES, null=True, blank=True)
    annee_diplome = models.CharField("Année d'obtention du diplôme", max_length=4, validators=[year_validator], null=True, blank=True)
    diplome_pdf = models.FileField(
        "Déposer votre diplôme (PDF)",
        upload_to='diplomes/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        null=True,
        blank=True
    )
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='en cours')

    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email + password suffisent

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
