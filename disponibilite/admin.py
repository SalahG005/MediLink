from django.contrib import admin
from .models import Disponibilite

@admin.register(Disponibilite)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ('medecin', 'date', 'heure_debut', 'heure_fin', 'disponible')
    list_filter = ('medecin', 'date', 'disponible')
    search_fields = ('medecin__first_name', 'medecin__last_name')
