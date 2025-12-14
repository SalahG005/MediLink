from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date
from rendezvous.models import RendezVous
import json

@login_required
def dashboard_medecin(request):
    today = date.today()
    
    # Tous les rendez-vous
    rdvs = RendezVous.objects.filter(disponibilite__medecin=request.user).order_by('disponibilite__date')
    rdvs_du_jour = rdvs.filter(disponibilite__date=today)
    
    # Préparer les événements pour le calendrier
    events = []
    for rdv in rdvs:
        # Exemple pour FullCalendar
        events.append({
    'title': f"{rdv.patient.get_full_name()} ({rdv.status})",
    'start': f"{rdv.disponibilite.date}T{rdv.disponibilite.heure_debut}",
    'color': '#0d6efd' if rdv.status == 'confirmed' else '#ffc107' if rdv.status == 'pending' else '#0dcaf0'
})

    # Préparer données pour le graphique des créneaux horaires
    time_slots = {}
    for rdv in rdvs:
        slot_hour = rdv.disponibilite.date.strftime("%H:00")  # <-- ici aussi
        time_slots[slot_hour] = time_slots.get(slot_hour, 0) + 1
    
    sorted_hours = sorted(time_slots.keys())
    counts = [time_slots[h] for h in sorted_hours]

    context = {
        'rdvs': rdvs,
        'stats': {
            'total_patients': rdvs_du_jour.count(),
            'patients_en_attente': rdvs.filter(status='pending').count(),
            'patients_reportes': rdvs.filter(status='rescheduled').count(),
            'patients_annules': rdvs.filter(status='canceled').count(),
        },
        'today': today.strftime("%Y-%m-%d"),
        'events_json': json.dumps(events),
        'time_labels': json.dumps(sorted_hours),
        'time_counts': json.dumps(counts),
    }

    return render(request, 'dashboard/dashboard_medecin.html', context)
