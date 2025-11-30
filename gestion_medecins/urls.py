from django.urls import path
from . import views

app_name = 'gestion_medecins'

urlpatterns = [
    path('', views.liste_medecins, name='liste_medecins'),
    path('medecin/<int:medecin_id>/', views.detail_medecin, name='detail_medecin'),
    path('medecin/<int:medecin_id>/valider/', views.valider_medecin, name='valider_medecin'),
    path('medecin/<int:medecin_id>/refuser/', views.refuser_medecin, name='refuser_medecin'),
]

