from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView, DeleteView

from .forms import PatientSignUpForm, MedecinSignUpForm, PatientUpdateForm, LoginForm
from .models import User
from gestion_medecins.models import Medecin
from specialite.models import Specialite


# Page d'accueil
def home(request):
    return render(request, 'users/home.html')

# Inscription Patient
def signup_patient(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirection après inscription
    else:
        form = PatientSignUpForm()
    return render(request, 'users/signup_patient.html', {'form': form})

# Inscription Médecin
def signup_medecin(request):
    if request.method == 'POST':
        form = MedecinSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirection après inscription
    else:
        form = MedecinSignUpForm()
    return render(request, 'users/signup_medecin.html', {'form': form})

# Connexion
def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, email=email, password=password)

        if user:
            if hasattr(user, 'etat_compte') and user.etat_compte == 'archive':
                error = "Votre compte a été archivé. Veuillez contacter l'administrateur."
                return render(request, 'users/signin.html', {'error': error})
            if user.role == 'medecin' and getattr(user, 'statut', '') != 'verifie':
                error = "Votre inscription est en cours de validation par l'administrateur."
                return render(request, 'users/signin.html', {'error': error})

        if user and user.role == role:
            login(request, user)
            if role == 'patient':
                return redirect('acceuil_patient')
            elif role == 'medecin':
                return redirect('dossiers:liste_dossiers')
            elif role == 'admin':
                return redirect('acceuil_admin')

        error = "Email, mot de passe ou rôle incorrect."
        return render(request, 'users/signin.html', {'error': error})

    return render(request, 'users/signin.html')


def logout_view(request):
    logout(request)
    return redirect('signin')

# Pages d'accueil spécifiques
def acceuil_patient(request):
    return render(request, 'users/acceuil_patient.html')

def acceuil_medecin(request):
    return render(request, 'users/acceuil_medecin.html')


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = PatientUpdateForm
    template_name = 'users/update_patient.html'
    success_url = reverse_lazy('acceuil_patient')  # après sauvegarde, redirection

    def get_object(self, queryset=None):
        # On retourne l'utilisateur connecté
        return self.request.user
    
class PatientDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/delete_patient.html'  # page de confirmation
    success_url = reverse_lazy('home')  # redirection après suppression

    def get_object(self, queryset=None):
        # Retourne uniquement l'utilisateur connecté
        return self.request.user

@login_required
def acceuil_admin(request):
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        messages.error(request, "Vous n'êtes pas autorisé à accéder à cette page.")
        return redirect('home')

    patients = User.objects.filter(role='patient')
    medecins_en_attente = Medecin.objects.filter(statut='en_attente').select_related('user')
    medecins_valides = Medecin.objects.filter(statut='valide').select_related('user')

    context = {
        'patients': patients,
        'medecins_en_attente': medecins_en_attente,
        'medecins_valides': medecins_valides,
    }
    return render(request, 'users/acceuil_admin.html', context)


@login_required
def archiver_patient(request, pk):
    # Check role
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    # Ensure POST method (from form)
    if request.method == 'POST':
        patient = get_object_or_404(User, pk=pk, role='patient')
        patient.etat_compte = 'archive'
        patient.save()
        messages.success(request, f"Le patient {patient.first_name} {patient.last_name} a été archivé.")
    return redirect('acceuil_admin')


@login_required
def supprimer_patient(request, pk):
    # Check role
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('home')

    if request.method == 'POST':
        patient = get_object_or_404(User, pk=pk, role='patient')
        patient.delete()
        messages.success(request, f"Le patient {patient.first_name} {patient.last_name} a été supprimé.")
    return redirect('acceuil_admin')

@login_required
def reactiver_patient(request, pk):
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        return redirect('home')

    if request.method == 'POST':
        patient = get_object_or_404(User, pk=pk, role='patient')
        patient.etat_compte = 'actif'
        patient.save()
    return redirect('acceuil_admin')

@login_required
def liste_medecins(request):
    """Liste uniquement les médecins validés + recherche + pagination avec filtres avancés"""

    medecins = Medecin.objects.filter(
        statut='valide'
    ).select_related('user', 'specialite')

    # -----------------------
    #     FILTERS
    # -----------------------
    specialite_filter = request.GET.get('specialite', '')
    gouvernorat_filter = request.GET.get('gouvernorat', '')
    ville_filter = request.GET.get('ville', '')

    if specialite_filter:
        medecins = medecins.filter(specialite__id_specialite=specialite_filter)

    if gouvernorat_filter:
        medecins = medecins.filter(user__gouvernorat=gouvernorat_filter)

    if ville_filter:
        medecins = medecins.filter(user__ville=ville_filter)

    # -----------------------
    #     ADVANCED SEARCH
    # -----------------------
    search_query = request.GET.get('search', '')
    if search_query:
        medecins = medecins.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(numero_ordre__icontains=search_query) |
            Q(telephone__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__gouvernorat__icontains=search_query) |
            Q(user__ville__icontains=search_query) |
            Q(specialite__nom_specialite__icontains=search_query)
        )

    # -----------------------
    #     PAGINATION
    # -----------------------
    paginator = Paginator(medecins, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # -----------------------
    #  DISTINCT FILTER VALUES
    # -----------------------
    gouvernorats = (
        User.objects.filter(role='medecin')
        .values_list('gouvernorat', flat=True)
        .distinct()
    )

    villes = (
        User.objects.filter(role='medecin')
        .values_list('ville', flat=True)
        .distinct()
    )

    context = {
        'medecins': page_obj,
        'search_query': search_query,
        'specialite_filter': specialite_filter,
        'gouvernorat_filter': gouvernorat_filter,
        'ville_filter': ville_filter,
        'specialites': Specialite.objects.all(),
        'gouvernorats': gouvernorats,
        'villes': villes,
    }

    return render(request, 'liste_medecins.html', context)

@login_required
def dashboard_admin(request):
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        return redirect('home')

    # Statistiques
    nb_patients_actifs = User.objects.filter(role='patient', etat_compte='actif').count()
    nb_patients_archives = User.objects.filter(role='patient', etat_compte='archive').count()
    nb_medecins_valide = Medecin.objects.filter(statut='valide').count()
    nb_medecins_en_attente = Medecin.objects.filter(statut='en_attente').count()
    nb_specialites = Specialite.objects.count()

    context = {
        'nb_patients_actifs': nb_patients_actifs,
        'nb_patients_archives': nb_patients_archives,
        'nb_medecins_valide': nb_medecins_valide,
        'nb_medecins_en_attente': nb_medecins_en_attente,
        'nb_specialites': nb_specialites,
        'medecins_en_attente': Medecin.objects.filter(statut='en_attente').select_related('user')
    }

    return render(request, 'users/dashboard_admin.html', context)
