from django import forms
from django.contrib.auth import get_user_model
from .models import Medecin


class MedecinAdminForm(forms.ModelForm):
    """Formulaire personnalisé pour l'admin permettant de créer un médecin avec juste un nom"""
    
    nom_medecin = forms.CharField(
        max_length=100,
        required=True,
        label="Nom du médecin",
        help_text="Entrez le nom complet du médecin (sera utilisé pour créer un utilisateur)"
    )
    
    class Meta:
        model = Medecin
        fields = ['numero_ordre', 'specialite', 'telephone', 'statut']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on modifie un médecin existant, pré-remplir le nom et rendre le champ optionnel
        if self.instance and self.instance.pk and self.instance.user:
            self.fields['nom_medecin'].initial = self.instance.user.get_full_name() or self.instance.user.username
            self.fields['nom_medecin'].required = False
            self.fields['nom_medecin'].help_text = "Laissez vide pour garder le nom actuel"
        else:
            # Pour la création, le nom est requis
            self.fields['nom_medecin'].required = True
    
    def save(self, commit=True):
        medecin = super().save(commit=False)
        nom_medecin = self.cleaned_data.get('nom_medecin', '').strip()
        
        if nom_medecin:
            # Créer ou récupérer un utilisateur
            if not medecin.user_id:
                # Créer un nouvel utilisateur
                username = nom_medecin.lower().replace(' ', '_')
                # S'assurer que le username est unique
                base_username = username
                counter = 1
                UserModel = get_user_model()
                while UserModel.objects.filter(email__iexact=f"{username}@medilink.local").exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                
                # Diviser le nom en prénom et nom si possible
                nom_parts = nom_medecin.split(' ', 1)
                if len(nom_parts) == 2:
                    first_name, last_name = nom_parts
                else:
                    first_name = nom_medecin
                    last_name = ''
                
                # Créer un nouvel utilisateur (jamais un superuser)
                user = UserModel.objects.create_user(
                    email=f"{username}@medilink.local",
                    first_name=first_name,
                    last_name=last_name,
                    password='medecin123',  # Mot de passe par défaut
                )
                user.role = 'medecin'
                user.save()
                medecin.user = user
            else:
                # Mettre à jour le nom de l'utilisateur existant
                nom_parts = nom_medecin.split(' ', 1)
                if len(nom_parts) == 2:
                    medecin.user.first_name = nom_parts[0]
                    medecin.user.last_name = nom_parts[1]
                else:
                    medecin.user.first_name = nom_medecin
                    medecin.user.last_name = ''
                medecin.user.role = 'medecin'
                medecin.user.save()
        
        if commit:
            medecin.save()
        return medecin

