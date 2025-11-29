from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_specialites, name='liste_specialites'),
    path('ajouter/', views.ajouter_specialite, name='ajouter_specialite'),
    path('modifier/<int:id>/', views.modifier_specialite, name='modifier_specialite'),
    path('supprimer/<int:id>/', views.supprimer_specialite, name='supprimer_specialite'),
    path('supprimer_selection/', views.supprimer_specialites_selectionnees, name='supprimer_specialites_selectionnees'),

]
