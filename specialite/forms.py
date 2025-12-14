from django import forms
from .models import Specialite

class SpecialiteForm(forms.ModelForm):
    class Meta:
        model = Specialite
        fields = ['nom_specialite', 'description']
