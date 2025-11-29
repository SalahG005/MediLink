from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, RendezVous
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, RendezVous, Notification
from django.contrib import messages


# 🗓️ PAGE PRINCIPALE DU CALENDRIER
# Cette fonction affiche tous les créneaux disponibles dans le calendrier.
@login_required
def calendrier(request):
    # On récupère les créneaux disponibles (is_available = True)
    slots = TimeSlot.objects.all()
    return render(request, 'rendezvous/calendrier.html', {'slots': slots})
    print(slots)  # ça doit afficher tous tes TimeSlot dans la console



# 📅 RÉSERVER UN RENDEZ-VOUS
# Cette fonction est appelée quand le patient clique sur un créneau pour le réserver.
@login_required
def prendre_rendezvous(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    print(f"DEBUG — Slot {slot.id} availability: {slot.is_available}")

    # 🔒 1️⃣ Check if the slot is already booked
    if not slot.is_available or RendezVous.objects.filter(slot=slot).exists():
        return render(request, 'rendezvous/message.html', {
            'message': "❌ Ce créneau est déjà réservé par un autre utilisateur."
        })

    try:
        # ✅ 2️⃣ Create the rendez-vous
        RendezVous.objects.create(
            patient=request.user,
            slot=slot,
            status='pending'
        )

        # ✅ 3️⃣ Mark the slot unavailable
        slot.is_available = False
        slot.save()

        return render(request, 'rendezvous/message.html', {
            'message': "✅ Rendez-vous pris avec succès !"
        })

    except Exception as e:
        print(f"ERREUR LORS DE LA RÉSERVATION: {e}")
        return render(request, 'rendezvous/message.html', {
            'message': "⚠️ Une erreur est survenue. Ce créneau est peut-être déjà pris."
        })

# 👤 MES RENDEZ-VOUS
# Cette fonction affiche tous les rendez-vous de l’utilisateur connecté.
@login_required
def mes_rendezvous(request):
    mes_rdv = RendezVous.objects.filter(patient=request.user).order_by('-booked_at')
    return render(request, 'rendezvous/mes_rendezvous.html', {'mes_rdv': mes_rdv})


# ❌ ANNULER UN RENDEZ-VOUS
# Cette fonction permet à un utilisateur d’annuler son rendez-vous.
@login_required
def annuler_rendezvous(request, rdv_id):
    # Vérifier que le rendez-vous appartient bien à l’utilisateur
    rdv = get_object_or_404(RendezVous, id=rdv_id, patient=request.user)

    # Mettre à jour le statut et libérer le créneau
    rdv.status = 'canceled'
    rdv.slot.is_available = True
    rdv.slot.save()
    rdv.save()

    # Redirection vers la page "Mes rendez-vous"
    return redirect('rendezvous:mes_rendezvous')

# 🕒 MODIFIER (REPORTER) UN RENDEZ-VOUS
@login_required
def modifier_rendezvous(request, rdv_id):
    # 1️⃣ Vérifier que le rendez-vous appartient à l’utilisateur
    rdv = get_object_or_404(RendezVous, id=rdv_id, patient=request.user)

    if request.method == 'POST':
        # 2️⃣ Récupérer le nouvel ID de créneau depuis le formulaire
        new_slot_id = request.POST.get('new_slot_id')
        new_slot = get_object_or_404(TimeSlot, id=new_slot_id)

        # Vérifier que le nouveau créneau est disponible
        if not new_slot.is_available or RendezVous.objects.filter(slot=new_slot).exists():
            return render(request, 'rendezvous/message.html', {
                'message': "❌ Ce nouveau créneau est déjà réservé."
            })

        # 3️⃣ Libérer l’ancien créneau
        rdv.slot.is_available = True
        rdv.slot.save()

        # 4️⃣ Réserver le nouveau créneau
        rdv.slot = new_slot
        new_slot.is_available = False
        new_slot.save()

        # 5️⃣ Mettre à jour le rendez-vous
        rdv.status = 'rescheduled'
        rdv.save()

        return render(request, 'rendezvous/message.html', {
            'message': "✅ Rendez-vous mis à jour avec succès !"
        })

    # Si GET → afficher la liste des créneaux disponibles
    available_slots = TimeSlot.objects.filter(is_available=True)
    return render(request, 'rendezvous/modifier_rendezvous.html', {
        'rdv': rdv,
        'available_slots': available_slots
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RendezVous, TimeSlot, Notification

# 🔹 Annuler un rendez-vous
@login_required
def medecin_annuler_rdv(request, rdv_id):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.status = 'canceled'
    rdv.slot.is_available = True
    rdv.slot.save()
    rdv.save()

    Notification.objects.create(
        user=rdv.patient,
        message=f"Votre rendez-vous du {rdv.slot.date.strftime('%Y-%m-%d %H:%M')} a été annulé par le médecin."
    )

    messages.success(request, "✅ Rendez-vous annulé et patient notifié.")
    return redirect('rendezvous:medecin_liste_rdv')


# 🔹 Valider un rendez-vous
@login_required
def medecin_valider_rdv(request, rdv_id):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.status = 'confirmed'
    rdv.save()

    Notification.objects.create(
        user=rdv.patient,
        message=f"Votre rendez-vous du {rdv.slot.date.strftime('%Y-%m-%d %H:%M')} a été confirmé par le médecin."
    )

    messages.success(request, "✅ Rendez-vous confirmé et patient notifié.")
    return redirect('rendezvous:medecin_liste_rdv')
    
@login_required
def medecin_reporter_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)

    if request.method == 'POST':
        new_slot_id = request.POST.get('slot_id')
        new_slot = get_object_or_404(TimeSlot, id=new_slot_id)

        # Vérifier que le créneau est disponible
        if RendezVous.objects.filter(slot=new_slot).exists():
            # Slot déjà utilisé → erreur ou message
            messages.error(request, "Ce créneau est déjà réservé.")
            return redirect('rendezvous:medecin_liste_rdv')

        # Libérer l'ancien slot
        rdv.slot.is_available = True
        rdv.slot.save()

        # Assigner le nouveau slot
        rdv.slot = new_slot
        rdv.status = 'rescheduled'
        rdv.save()

        # Marquer le nouveau slot comme occupé
        new_slot.is_available = False
        new_slot.save()

        messages.success(request, "Rendez-vous reporté avec succès.")
        return redirect('rendezvous:medecin_liste_rdv')

    # GET → afficher le formulaire avec slots disponibles
    available_slots = TimeSlot.objects.filter(is_available=True)
    return render(request, 'rendezvousmedecin/modifier_rdv_medecin.html', {
        'rdv': rdv,
        'available_slots': available_slots
    })


# 🔹 Liste des rendez-vous côté médecin
@login_required
def medecin_liste_rdv(request):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    rdvs = RendezVous.objects.all().order_by('slot__date')
    return render(request, 'rendezvousmedecin/medecin_liste_rdv.html', {'rdvs': rdvs})


# 🔹 Détails d'un rendez-vous côté médecin
@login_required
def medecin_detail_rdv(request, rdv_id):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    rdv = get_object_or_404(RendezVous, id=rdv_id)
    return render(request, 'rendezvousmedecin/medecin_detail_rdv.html', {'rdv': rdv})


