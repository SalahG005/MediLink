from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DossierMedicalForm, PatientForm
from .models import DossierMedical, Patient


@login_required
def liste_dossiers(request):
    """Liste tous les dossiers médicaux"""
    dossiers = DossierMedical.objects.select_related('patient__user', 'medecin').all()

    # Recherche par nom de patient
    search_query = request.GET.get('search', '')
    if search_query:
        dossiers = dossiers.filter(
            Q(patient__nom__icontains=search_query)
            | Q(patient__prenom__icontains=search_query)
            | Q(patient__user__first_name__icontains=search_query)
            | Q(patient__user__last_name__icontains=search_query)
            | Q(patient__user__email__icontains=search_query)
        )
    
    paginator = Paginator(dossiers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'dossiers': page_obj,
        'search_query': search_query,
    }
    return render(request, 'dossiers/liste_dossiers.html', context)


@login_required
def consulter_dossier(request, dossier_id):
    """Consulter un dossier médical"""
    dossier = get_object_or_404(DossierMedical, id=dossier_id)
    context = {
        'dossier': dossier,
    }
    return render(request, 'dossiers/consulter_dossier.html', context)


@login_required
def ajouter_dossier(request):
    """Ajouter un nouveau dossier médical"""
    patient_id = request.GET.get('patient')
    initial = {}
    if patient_id:
        try:
            patient = Patient.objects.get(id=patient_id)
            initial['patient'] = patient
        except Patient.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = DossierMedicalForm(request.POST)
        if form.is_valid():
            dossier = form.save(commit=False)
            if hasattr(request, 'user') and request.user.is_authenticated and getattr(request.user, 'role', None) == 'medecin':
                dossier.medecin = request.user
            dossier.save()
            messages.success(request, 'Dossier médical ajouté avec succès.')
            return redirect('dossiers:liste_dossiers')
    else:
        form = DossierMedicalForm(initial=initial)
    
    context = {
        'form': form,
        'title': 'Ajouter un dossier médical',
    }
    return render(request, 'dossiers/form_dossier.html', context)


@login_required
def modifier_dossier(request, dossier_id):
    """Modifier un dossier médical existant"""
    dossier = get_object_or_404(DossierMedical, id=dossier_id)
    
    if request.method == 'POST':
        form = DossierMedicalForm(request.POST, instance=dossier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dossier médical modifié avec succès.')
            return redirect('dossiers:consulter_dossier', dossier_id=dossier.id)
    else:
        form = DossierMedicalForm(instance=dossier)
    
    context = {
        'form': form,
        'dossier': dossier,
        'title': 'Modifier le dossier médical',
    }
    return render(request, 'dossiers/form_dossier.html', context)


@login_required
def liste_patients(request):
    """Liste tous les patients"""
    patients = Patient.objects.select_related('user').all()

    search_query = request.GET.get('search', '')
    if search_query:
        patients = patients.filter(
            nom__icontains=search_query
        ) | patients.filter(
            prenom__icontains=search_query
        ) | patients.filter(
            user__first_name__icontains=search_query
        ) | patients.filter(
            user__last_name__icontains=search_query
        ) | patients.filter(
            user__email__icontains=search_query
        )

    paginator = Paginator(patients, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'patients': page_obj,
        'search_query': search_query,
    }
    return render(request, 'dossiers/liste_patients.html', context)


@login_required
def ajouter_patient(request):
    """Ajouter un nouveau patient"""
    messages.info(
        request,
        "Les patients sont désormais créés automatiquement lors de l'inscription."
    )
    return redirect('dossiers:liste_patients')
