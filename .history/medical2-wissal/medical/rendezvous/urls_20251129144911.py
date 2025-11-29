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
    
        # 🔹 Côté médecin
    path('medecin/annuler/<int:rdv_id>/', views.medecin_annuler_rdv, name='medecin_annuler_rdv'),
    path('medecin/valider/<int:rdv_id>/', views.medecin_valider_rdv, name='medecin_valider_rdv'),
    path('medecin/reporter/<int:rdv_id>/', views.medecin_reporter_rdv, name='medecin_reporter_rdv'),
    # Côté médecin
    path('medecin/rendezvous/', views.medecin_liste_rdv, name='medecin_liste_rdv'),
    path('medecin/rendezvous/<int:rdv_id>/', views.medecin_detail_rdv, name='medecin_detail_rdv'),
    path('notifications/', views.get_notifications, name='get_notifications'),

]
