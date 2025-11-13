from django import forms
from .models import User
from specialite.models import Specialite

class PatientSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    date_of_birth = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'JJ/MM/AAAA'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password',
                  'phone', 'date_of_birth', 'gouvernorat', 'ville']
      

    specialite = forms.ModelChoiceField(
        queryset=Specialite.objects.all(),
        empty_label="Choisissez une spécialité",
        required=True
)
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        
        if password != confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class MedecinSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirmer le mot de passe")
    date_of_birth = forms.DateField(
        input_formats=['%d/%m/%Y'],
        widget=forms.DateInput(format='%d/%m/%Y', attrs={'placeholder': 'JJ/MM/AAAA'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password',
                  'phone', 'date_of_birth', 'specialite', 'annee_diplome', 'diplome_pdf',
                  'code_postal', 'gouvernorat', 'ville']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm_password')
        if password != confirm:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'medecin'
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")
    
class PatientUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        # Ici, les champs que le patient peut mettre à jour
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'gouvernorat', 'ville']
