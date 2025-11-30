from django import forms
from .models import DossierMedical, Patient


class PatientForm(forms.ModelForm):
    """Formulaire pour créer/modifier un patient"""
    
    class Meta:
        model = Patient
        fields = ['nom', 'prenom', 'date_naissance', 'sexe', 'telephone', 'adresse', 'numero_carte_identite']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse'}),
            'numero_carte_identite': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de carte d\'identité'}),
        }
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'date_naissance': 'Date de naissance',
            'sexe': 'Sexe',
            'telephone': 'Téléphone',
            'adresse': 'Adresse',
            'numero_carte_identite': 'Numéro de carte d\'identité',
        }


class DossierMedicalForm(forms.ModelForm):
    """Formulaire pour créer/modifier un dossier médical"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.select_related('user').order_by('user__last_name', 'user__first_name')
        self.fields['patient'].label_from_instance = lambda patient: patient.user.get_full_name() or patient.user.email
    
    class Meta:
        model = DossierMedical
        fields = ['patient', 'motif_consultation', 'diagnostic', 'traitement', 'observations', 'allergies', 'antecedents']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'motif_consultation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motif de consultation'}),
            'diagnostic': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Diagnostic'}),
            'traitement': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Traitement prescrit'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observations'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Allergies connues'}),
            'antecedents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Antécédents médicaux'}),
        }
        labels = {
            'patient': 'Patient',
            'motif_consultation': 'Motif de consultation',
            'diagnostic': 'Diagnostic',
            'traitement': 'Traitement prescrit',
            'observations': 'Observations',
            'allergies': 'Allergies connues',
            'antecedents': 'Antécédents médicaux',
        }


