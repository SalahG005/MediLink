from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from disponibilite.models import Disponibilite
from .models import RendezVous, Notification
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.models import User
from .models import RendezVous, Disponibilite

@login_required
def choisir_medecin(request):
    medecins = User.objects.filter(role='medecin', statut='verifie').order_by('first_name')
    # On compte les créneaux disponibles
    medecins_with_counts = []
    for m in medecins:
        count = Disponibilite.objects.filter(medecin=m, disponible=True).count()
        medecins_with_counts.append({'medecin': m, 'available_count': count})
    return render(request, 'rendezvous/choisir_medecin.html', {'medecins': medecins_with_counts})


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
    rdv = get_object_or_404(RendezVous, id=rdv_id, patient=request.user)

    # 🔔 notifier le médecin
    Notification.objects.create(
        user=rdv.disponibilite.medecin,
        message=f"Le patient {request.user.get_full_name()} a annulé son rendez-vous du {rdv.disponibilite.date}."
    )

    rdv.status = 'canceled'
    rdv.disponibilite.disponible = True
    rdv.disponibilite.save()
    rdv.save()

    return redirect('rendezvous:mes_rendezvous')


# 🕒 MODIFIER (REPOR@login_required
def modifier_rendezvous(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id, patient=request.user)

    if request.method == 'POST':
        new_dispo_id = request.POST.get('new_dispo_id')
        new_dispo = get_object_or_404(Disponibilite, id=new_dispo_id, disponible=True)

        rdv.disponibilite.disponible = True
        rdv.disponibilite.save()

        rdv.disponibilite = new_dispo
        rdv.status = 'rescheduled'
        new_dispo.disponible = False
        new_dispo.save()
        rdv.save()

        Notification.objects.create(
            user=new_dispo.medecin,
            message=f"Le patient {request.user.get_full_name()} a reporté son rendez-vous."
        )

        return render(request, 'rendezvous/message.html', {
            'message': "✅ Rendez-vous reporté avec succès."
        })

    disponibilites = Disponibilite.objects.filter(disponible=True)
    return render(request, 'rendezvous/modifier_rendezvous.html', {
        'rdv': rdv,
        'disponibilites': disponibilites
    })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RendezVous, Disponibilite, Notification

# 🔹 Annuler un rendez-vous
@login_required
def medecin_annuler_rdv(request, rdv_id):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    rdv = get_object_or_404(RendezVous, id=rdv_id)
    rdv.status = 'canceled'
    rdv.disponibilite.disponible = True
    rdv.disponibilite.save()
    rdv.save()

    Notification.objects.create(
        user=rdv.patient,
        message=f"Votre rendez-vous du {rdv.disponibilite.date.strftime('%Y-%m-%d %H:%M')} a été annulé par le médecin."
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
        message=f"Votre rendez-vous du {rdv.disponibilite.date.strftime('%Y-%m-%d %H:%M')} a été confirmé par le médecin."
    )

    messages.success(request, " Rendez-vous confirmé et patient notifié.")
    return redirect('rendezvous:medecin_liste_rdv')

@login_required
def medecin_reporter_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)

    if request.method == 'POST':
        new_dispo_id = request.POST.get('new_dispo_id')
        new_dispo = get_object_or_404(Disponibilite, id=new_dispo_id, disponible=True)


        # Vérifier que le créneau est disponible
        if RendezVous.objects.filter(disponibilite=new_dispo).exists():

            messages.error(request, "Ce créneau est déjà réservé.")
            return redirect('rendezvous:medecin_liste_rdv')

        rdv.disponibilite.disponible = True
        rdv.disponibilite.save()

        rdv.disponibilite = new_dispo
        rdv.status = 'rescheduled'
        rdv.save()

        new_dispo.disponible = False
        new_dispo.save()
        messages.success(request, "Rendez-vous reporté avec succès.")
        return redirect('rendezvous:medecin_liste_rdv')

    available_disponibilites = Disponibilite.objects.filter(disponible=True)

    return render(request, 'rendezvousmedecin/modifier_rdv_medecin.html', {
    'rdv': rdv,
    'available_disponibilites': available_disponibilites
})



# 🔹 Liste des rendez-vous côté médecin
@login_required
def medecin_liste_rdv(request):
    if request.user.role != 'medecin':
        return redirect('rendezvous:calendrier')

    # Only show appointments that belong to the logged in doctor
    rdvs = RendezVous.objects.filter(disponibilite__medecin=request.user).order_by('disponibilite__date')

    # Notifications for the doctor (latest first)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'rdvs': rdvs,
        'notifications': notifications,
        'unread_count': unread_count,
    }

    return render(request, 'rendezvousmedecin/medecin_liste_rdv.html', context)


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
from django.shortcuts import render

from django.shortcuts import render, redirect

@login_required
def medecin_slots(request, medecin_id):
    # Redirection vers le calendrier du médecin choisi
    return redirect('rendezvous:calendrier', medecin_id=medecin_id)
@login_required
@login_required
def prendre_rendezvous(request, dispo_id):
    dispo = get_object_or_404(Disponibilite, id=dispo_id)
    
    # Vérifie si un rendez-vous existe déjà pour cette dispo
    if RendezVous.objects.filter(disponibilite=dispo).exists():
        messages.error(request, "Ce créneau est déjà réservé.")
        return redirect('rendezvous:choisir_medecin')  # ou la page calendrier

    rdv = RendezVous.objects.create(
        patient=request.user,
        disponibilite=dispo
    )

    # marque la dispo comme non-disponible
    dispo.disponible = False
    dispo.save()

    messages.success(request, "Rendez-vous pris avec succès !")
    return redirect('rendezvous:mes_rendezvous')
def mark_as_read(request, notif_id):
    return redirect('rendezvous:get_notifications')

def mark_all_read(request):
    return redirect('rendezvous:get_notifications')
@login_required
def calendrier(request, medecin_id=None):
    if medecin_id is None:
        # Si aucun médecin choisi, prendre le premier
        medecin = User.objects.filter(role='medecin').first()
    else:
        medecin = get_object_or_404(User, id=medecin_id, role='medecin')

    return render(request, 'rendezvous/calendrier.html', {'medecin': medecin})
@login_required
def disponibilite_patient_json(request, medecin_id):
    medecin = get_object_or_404(User, id=medecin_id, role='medecin')
    slots = Disponibilite.objects.filter(medecin=medecin, disponible=True)

    events = []
    for slot in slots:
        events.append({
            'id': slot.id,
            'title': f"{slot.medecin.get_full_name()}",  # parenthèses !
            'start': f"{slot.date}T{slot.heure_debut}",
            'end': f"{slot.date}T{slot.heure_fin}",
        })
    return JsonResponse(events, safe=False)
