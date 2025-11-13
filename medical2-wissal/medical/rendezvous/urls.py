#ADDED THIS URLLLLLLLLL
from django.urls import path
from . import views

app_name = 'rendezvous'  # ✅ AJOUTE CETTE LIGNE

urlpatterns = [
    path('calendrier/', views.calendrier, name='calendrier'),
    path('prendre/<int:slot_id>/', views.prendre_rendezvous, name='prendre_rendezvous'),
    path('mes-rendezvous/', views.mes_rendezvous, name='mes_rendezvous'),
    path('annuler/<int:rdv_id>/', views.annuler_rendezvous, name='cancel_rdv'),
    path('modifier/<int:rdv_id>/', views.modifier_rendezvous, name='modifier_rendezvous'),


]
