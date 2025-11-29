from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, RendezVous
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, RendezVous, Notification
from django.contrib import messages

# ✳️ NOUVELLE ÉTAPE — CHOISIR UN MÉDECIN
@login_required
def choisir_medecin(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    medecins = User.objects.filter(role='medecin', statut='verifie').order_by('first_name', 'last_name')
    medecins_with_counts = []
    for m in medecins:
        available_count = TimeSlot.objects.filter(medecin=m, is_available=True).count()
        medecins_with_counts.append({'medecin': m, 'available_count': available_count})

    return render(request, 'rendezvous/choisir_medecin.html', {'medecins': medecins_with_counts})


# ✳️ AFFICHER LES CRÉNEAUX D'UN MÉDECIN SÉLECTIONNÉ
@login_required
def medecin_slots(request, medecin_id):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    medecin = get_object_or_404(User, id=medecin_id, role='medecin')
    slots = TimeSlot.objects.filter(medecin=medecin, is_available=True).order_by('date')

    return render(request, 'rendezvous/medecin_slots.html', {'medecin': medecin, 'slots': slots})


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
        rendezvous = RendezVous.objects.create(
            patient=request.user,
            slot=slot,
            status='pending'
        )

        # 🔔 3️⃣ Create notification BEFORE returning the response
        Notification.objects.create(
            user=slot.medecin,
            message=f"Le patient {request.user.first_name} {request.user.last_name} a pris rendez-vous le {slot.date}."
        )

        # ❌ 4️⃣ Mark the slot unavailable
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

    # If the slot has a medecin associated, notify them about the cancellation.
    if getattr(rdv, 'slot', None) and getattr(rdv.slot, 'medecin', None):
        Notification.objects.create(
            user=rdv.slot.medecin,
            message=f"Le patient {request.user.first_name} {request.user.last_name} a annulé son rendez-vous prévu le {rdv.slot.date.strftime('%Y-%m-%d %H:%M')}."
        )


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

        # 🔔 notiff

        Notification.objects.create(
    user=new_slot.medecin,
    message=f"Le patient {request.user.first_name} {request.user.last_name} a modifié son rendez-vous au {new_slot.date}."
)


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

    messages.success(request, " Rendez-vous confirmé et patient notifié.")
    return redirect('rendezvous:medecin_liste_rdv')

@login_required
def medecin_reporter_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)

    if request.method == 'POST':
        new_slot_id = request.POST.get('new_slot_id')  # ← corrigé
        new_slot = get_object_or_404(TimeSlot, id=new_slot_id)

        # Vérifier que le créneau est disponible
        if RendezVous.objects.filter(slot=new_slot).exists():
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


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    notif_list = []
    for n in notifications:
        notif_list.append({
            'id': n.id,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'notifications': notif_list})


from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Notification

@login_required
@csrf_exempt
def mark_as_read(request, notif_id):
    if request.method == "POST":
        try:
            notif = Notification.objects.get(id=notif_id, user=request.user)
            notif.is_read = True
            notif.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Fonction séparée, **pas indentée à l’intérieur de mark_as_read**
@login_required
@csrf_exempt
def mark_all_read(request):
    if request.method == "POST":
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({"status": "ok"})
    return JsonResponse({'status': 'failed', 'error': 'Invalid request'})
