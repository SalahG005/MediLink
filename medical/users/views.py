from django.shortcuts import render, redirect
from .forms import PatientSignUpForm, MedecinSignUpForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import DeleteView
from .forms import PatientSignUpForm, MedecinSignUpForm, PatientUpdateForm, LoginForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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

        if user and user.role == role:
            login(request, user)
            if role == 'patient':
                return redirect('acceuil_patient')
            elif role == 'medecin':
                return redirect('acceuil_medecin')
            elif role == 'admin':
                return redirect('acceuil_admin')

        error = "Email, mot de passe ou rôle incorrect."
        return render(request, 'users/signin.html', {'error': error})

    return render(request, 'users/signin.html')

# Pages d'accueil spécifiques
def acceuil_patient(request):
    return render(request, 'users/acceuil_patient.html')

def acceuil_medecin(request):
    return render(request, 'users/acceuil_medecin.html')


from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from .models import User
from .forms import PatientUpdateForm

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

    # Show all patients
    patients = User.objects.filter(role='patient')
    return render(request, 'users/acceuil_admin.html', {'patients': patients})


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

