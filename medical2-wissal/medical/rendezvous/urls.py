#ADDED THIS URLLLLLLLLL
from django.urls import path
from . import views

app_name = 'rendezvous'  # ✅ AJOUTE CETTE LIGNE

urlpatterns = [
    path('calendrier/', views.calendrier, name='calendrier'),
    # étape 1 → choisir un médecin
    path('choisir-medecin/', views.choisir_medecin, name='choisir_medecin'),
    # étape 2 → voir les créneaux pour le médecin choisi
    path('medecin/<int:medecin_id>/slots/', views.medecin_slots, name='medecin_slots'),
    path('prendre/<int:slot_id>/', views.prendre_rendezvous, name='prendre_rendezvous'),
    path('mes-rendezvous/', views.mes_rendezvous, name='mes_rendezvous'),
    path('annuler/<int:rdv_id>/', views.annuler_rendezvous, name='cancel_rdv'),
    path('modifier/<int:rdv_id>/', views.modifier_rendezvous, name='modifier_rendezvous'),
    
        # 🔹 Côté médecin
    path('medecin/annuler/<int:rdv_id>/', views.medecin_annuler_rdv, name='medecin_annuler_rdv'),
    path('medecin/valider/<int:rdv_id>/', views.medecin_valider_rdv, name='medecin_valider_rdv'),
    path('medecin/reporter/<int:rdv_id>/', views.medecin_reporter_rdv, name='medecin_reporter_rdv'),
    # Côté médecin
    path('medecin/rendezvous/', views.medecin_liste_rdv, name='medecin_liste_rdv'),
    path('medecin/rendezvous/<int:rdv_id>/', views.medecin_detail_rdv, name='medecin_detail_rdv'),
   path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/mark_read/<int:notif_id>/', views.mark_as_read, name='mark_read'),
    path('notifications/mark_all_read/', views.mark_all_read, name='mark_all_read'),


]
