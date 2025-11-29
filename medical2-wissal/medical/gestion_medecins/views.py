from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Medecin
from django.db.models import Q


def _ensure_admin(request):
    if not request.user.is_authenticated or getattr(request.user, 'role', None) != 'admin':
        messages.error(request, "Accès refusé.")
        return False
    return True


@login_required
def liste_medecins(request):
    """Liste tous les médecins avec leur statut"""
    if not _ensure_admin(request):
        return redirect('home')

    medecins = Medecin.objects.all().select_related('user')

    # Filtre par statut
    statut_filter = request.GET.get('statut', '')
    if statut_filter:
        medecins = medecins.filter(statut=statut_filter)

    # Recherche
    search_query = request.GET.get('search', '')
    if search_query:
        medecins = medecins.filter(
            Q(user__first_name__icontains=search_query)
            | Q(user__last_name__icontains=search_query)
            | Q(user__email__icontains=search_query)
            | Q(specialite__icontains=search_query)
        )

    paginator = Paginator(medecins, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'medecins': page_obj,
        'search_query': search_query,
        'statut_filter': statut_filter,
        'statut_choices': Medecin.STATUT_CHOICES,
    }
    return render(request, 'gestion_medecins/liste_medecins.html', context)


@login_required
def valider_medecin(request, medecin_id):
    """Valider l'inscription d'un médecin"""
    if not _ensure_admin(request):
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée.")
        return redirect('gestion_medecins:liste_medecins')

    medecin = get_object_or_404(Medecin, id=medecin_id)

    if medecin.statut == 'en_attente':
        medecin.statut = 'valide'
        medecin.date_validation = timezone.now()
        medecin.save()
        medecin.user.statut = 'verifie'
        medecin.user.save(update_fields=['statut'])
        messages.success(request, f'L\'inscription du médecin {medecin.user.get_full_name()} a été validée.')
    else:
        messages.warning(request, 'Ce médecin a déjà été traité.')

    return redirect('gestion_medecins:liste_medecins')


@login_required
def refuser_medecin(request, medecin_id):
    """Refuser l'inscription d'un médecin"""
    if not _ensure_admin(request):
        return redirect('home')

    if request.method != 'POST':
        messages.error(request, "Méthode non autorisée.")
        return redirect('gestion_medecins:liste_medecins')

    medecin = get_object_or_404(Medecin, id=medecin_id)

    if medecin.statut == 'en_attente':
        medecin.statut = 'refuse'
        medecin.save()
        medecin.user.statut = 'exclu'
        medecin.user.save(update_fields=['statut'])
        messages.success(request, f'L\'inscription du médecin {medecin.user.get_full_name()} a été refusée.')
    else:
        messages.warning(request, 'Ce médecin a déjà été traité.')

    return redirect('gestion_medecins:liste_medecins')


@login_required
def detail_medecin(request, medecin_id):
    """Afficher les détails d'un médecin"""
    if not _ensure_admin(request):
        return redirect('home')

    medecin = get_object_or_404(Medecin, id=medecin_id)

    context = {
        'medecin': medecin,
    }
    return render(request, 'gestion_medecins/detail_medecin.html', context)
