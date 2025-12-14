from django.contrib import admin
from .models import Patient, DossierMedical


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'nom', 'prenom', 'date_naissance', 'sexe', 'telephone', 'date_creation')
    search_fields = ('nom', 'prenom', 'numero_carte_identite', 'telephone', 'user__email', 'user__first_name', 'user__last_name')
    list_filter = ('sexe', 'date_creation')
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('user', 'nom', 'prenom', 'date_naissance', 'sexe', 'numero_carte_identite')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'adresse')
        }),
        ('Dates', {
            'fields': ('date_creation',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('date_creation',)
    ordering = ('nom', 'prenom')


@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_consultation', 'diagnostic', 'date_modification')
    search_fields = ('patient__nom', 'patient__prenom', 'diagnostic', 'motif_consultation', 'traitement')
    list_filter = ('date_consultation', 'medecin', 'date_modification')
    readonly_fields = ('date_consultation', 'date_modification')
    fieldsets = (
        ('Informations générales', {
            'fields': ('patient', 'medecin', 'date_consultation', 'date_modification')
        }),
        ('Informations médicales', {
            'fields': ('motif_consultation', 'diagnostic', 'traitement')
        }),
        ('Informations complémentaires', {
            'fields': ('observations', 'allergies', 'antecedents'),
            'classes': ('collapse',)
        }),
    )
    ordering = ('-date_consultation',)
    date_hierarchy = 'date_consultation'
