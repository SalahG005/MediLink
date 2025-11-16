from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import Disponibilite
from datetime import date, timedelta, datetime, time

# Affichage du calendrier
class CalendarView(View):
    def get(self, request):
        return render(request, "disponibilite/calendar.html")


# JSON pour FullCalendar avec jours fériés et week-ends
JOURS_FERIES = {
    "2025-01-01": "Jour de l’An",
    "2025-03-20": "Fête de l’Indépendance",
    "2025-03-30": "Aïd al‑Fitr (début)",
    "2025-03-31": "Aïd al‑Fitr (fin)",
    "2025-04-09": "Journée des Martyrs",
    "2025-05-01": "Fête du Travail",
    "2025-06-06": "Aïd al‑Adha (Fête du Sacrifice)",
    "2025-06-26": "Nouvel An de l’Hégire (Ras el Am)",
    "2025-07-25": "Fête de la République",
    "2025-08-13": "Fête de la Femme",
    "2025-09-04": "Mouled (Naissance du Prophète)",
    "2025-10-15": "Fête de l’Évacuation",
    "2025-12-17": "Fête de la Révolution",
}

class DisponibiliteJson(View):
    def get(self, request):
        disponibilites = Disponibilite.objects.all()
        events = []

        # Disponibilités existantes
        for dispo in disponibilites:
            events.append({
                "id": dispo.id,
                "title": dispo.medecin.get_full_name(),  # Nom du médecin
                "start": f"{dispo.date}T{dispo.heure_debut}",
                "end": f"{dispo.date}T{dispo.heure_fin}",
                "color": "green" if dispo.disponible else "red",
                "editable": True
            })

        # Ajouter week-ends et jours fériés
        today = date.today()
        for i in range(-30, 365):
            d = today + timedelta(days=i)
            if d.weekday() in [5,6]:  # samedi ou dimanche
                events.append({
                    "title": "Weekend",
                    "start": str(d),
                    "allDay": True,
                    "color": "#f8d7da",
                    "editable": False
                })
            if str(d) in JOURS_FERIES:
                events.append({
                    "title": f"Jour férié: {JOURS_FERIES[str(d)]}",
                    "start": str(d),
                    "allDay": True,
                    "color": "#f8d7da",
                    "editable": False
                })

        return JsonResponse(events, safe=False)


# Ajouter un créneau
class DisponibiliteAdd(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Utilisateur non connecté"})

        date_str = request.POST.get('date')
        heure_debut = request.POST.get('heure_debut')
        heure_fin = request.POST.get('heure_fin')

        start_time = datetime.strptime(heure_debut, "%H:%M").time()
        end_time = datetime.strptime(heure_fin, "%H:%M").time()

        weekday = datetime.strptime(date_str, "%Y-%m-%d").weekday()
        if weekday == 6:
            return JsonResponse({"status": "error", "message": "Ajout interdit le dimanche"})
        if weekday == 5 and start_time >= time(14,0):
            return JsonResponse({"status": "error", "message": "Ajout interdit après 14h le samedi"})

        dispo = Disponibilite.objects.create(
            medecin=request.user,  # <-- médecin connecté
            date=date_str,
            heure_debut=start_time,
            heure_fin=end_time,
            disponible=True
        )
        return JsonResponse({"status": "ok", "id": dispo.id})


# Supprimer un créneau
class DisponibiliteDelete(View):
    def post(self, request, dispo_id):
        try:
            dispo = Disponibilite.objects.get(id=dispo_id)
            del_start_str = request.POST.get('heure_debut')
            del_end_str = request.POST.get('heure_fin')

            if not del_start_str or not del_end_str:
                dispo.delete()
                return JsonResponse({"status": "ok"})

            del_start = datetime.strptime(del_start_str, '%H:%M').time()
            del_end = datetime.strptime(del_end_str, '%H:%M').time()

            if del_start <= dispo.heure_debut and del_end >= dispo.heure_fin:
                dispo.delete()
            elif del_start <= dispo.heure_debut < del_end < dispo.heure_fin:
                dispo.heure_debut = del_end
                dispo.save()
            elif dispo.heure_debut < del_start < dispo.heure_fin <= del_end:
                dispo.heure_fin = del_start
                dispo.save()
            elif dispo.heure_debut < del_start and del_end < dispo.heure_fin:
                new_dispo = Disponibilite.objects.create(
                    medecin=dispo.medecin,
                    date=dispo.date,
                    heure_debut=del_end,
                    heure_fin=dispo.heure_fin,
                    disponible=True
                )
                dispo.heure_fin = del_start
                dispo.save()

            return JsonResponse({"status": "ok"})
        except Disponibilite.DoesNotExist:
            return JsonResponse({"status": "error"})


# Modifier un créneau
class DisponibiliteUpdate(View):
    def post(self, request, dispo_id):
        try:
            dispo = Disponibilite.objects.get(id=dispo_id)
            dispo.date = request.POST.get('date', dispo.date)
            dispo.heure_debut = request.POST.get('heure_debut', dispo.heure_debut)
            dispo.heure_fin = request.POST.get('heure_fin', dispo.heure_fin)
            dispo.save()
            return JsonResponse({"status": "ok"})
        except Disponibilite.DoesNotExist:
            return JsonResponse({"status": "error"})
