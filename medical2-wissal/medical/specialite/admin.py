from django.contrib import admin
from .models import Specialite

@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ('id_specialite', 'nom_specialite', 'description')
