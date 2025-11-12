from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.liste_dossiers, name='liste_dossiers'),
    path('dossier/<int:dossier_id>/', views.consulter_dossier, name='consulter_dossier'),
    path('dossier/ajouter/', views.ajouter_dossier, name='ajouter_dossier'),
    path('dossier/<int:dossier_id>/modifier/', views.modifier_dossier, name='modifier_dossier'),
    path('patients/', views.liste_patients, name='liste_patients'),
    path('patients/ajouter/', views.ajouter_patient, name='ajouter_patient'),
]

