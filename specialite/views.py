from django.shortcuts import render, redirect, get_object_or_404
from .models import Specialite
from .forms import SpecialiteForm
from django.contrib import messages

# 🟢 Afficher la liste des spécialités
def liste_specialites(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'nom_specialite')  # tri par défaut sur le nom

    # Filtrage
    specialites = Specialite.objects.all()
    if search_query:
        specialites = specialites.filter(nom_specialite__icontains=search_query)

    

    return render(request, 'specialite/liste.html', {
        'specialites': specialites,
        'search_query': search_query,
    })

# 🟢 Ajouter une spécialité
def ajouter_specialite(request):
    specialites = Specialite.objects.all()  # 🔹 Récupérer toutes les spécialités
    if request.method == 'POST':
        form = SpecialiteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('ajouter_specialite')  # redirige vers la même page pour voir le formulaire + liste
    else:
        form = SpecialiteForm()
    return render(request, 'specialite/ajouter.html', {
        'form': form,
        'specialites': specialites,
        'specialite': None  # pour le template (indique qu'on est en mode ajout)
    })


# 🟢 Modifier une spécialité
# 🟢 Modifier une spécialité
def modifier_specialite(request, id):
    specialite = get_object_or_404(Specialite, id_specialite=id)
    if request.method == 'POST':
        form = SpecialiteForm(request.POST, instance=specialite)
        if form.is_valid():
            form.save()
            # 🔹 Redirection vers la liste après modification
            return redirect('liste_specialites')
    else:
        form = SpecialiteForm(instance=specialite)
    # 🔹 On envoie aussi toutes les spécialités pour la liste à gauche
    specialites = Specialite.objects.all()
    return render(request, 'specialite/modifier.html', {
        'form': form,
        'specialite': specialite,
        'specialites': specialites  # pour la liste à gauche
    })


# 🟢 Supprimer une spécialité
def supprimer_specialite(request, id):
    specialite = get_object_or_404(Specialite, id_specialite=id)
    if request.method == 'POST':
        specialite.delete()
        return redirect('liste_specialites')
    return render(request, 'specialite/supprimer.html', {'specialite': specialite})


# 🟢 Supprimer plusieurs spécialités
def supprimer_specialites_selectionnees(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_ids')
        if ids:
            Specialite.objects.filter(id_specialite__in=ids).delete()
            messages.success(request, f"{len(ids)} spécialité(s) supprimée(s) avec succès.")
        else:
            messages.warning(request, "Aucune spécialité sélectionnée.")
    return redirect('liste_specialites')
