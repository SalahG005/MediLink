from django.shortcuts import render, redirect
from .forms import PatientSignUpForm, MedecinSignUpForm
from django.contrib.auth import authenticate, login
from django.views.generic.edit import DeleteView
from .forms import PatientSignUpForm, MedecinSignUpForm, PatientUpdateForm, LoginForm


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
        role = request.POST.get('role')  # récupère le choix radio

        user = authenticate(request, email=email, password=password)
        if user and user.role == role:
            login(request, user)
            # Redirection selon rôle
            if role == 'patient':
                return redirect('acceuil_patient')
            else:
                return redirect('acceuil_medecin')
        else:
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
