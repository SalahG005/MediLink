from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import Medecin
from .forms import MedecinAdminForm


@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    form = MedecinAdminForm
    list_display = ('user', 'specialite', 'numero_ordre', 'telephone', 'statut', 'date_inscription', 'date_validation')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'specialite', 'numero_ordre', 'telephone')
    list_filter = ('statut', 'date_inscription', 'specialite')
    readonly_fields = ('date_inscription', 'date_validation')
    fieldsets = (
        ('Informations du médecin', {
            'fields': ('nom_medecin',)
        }),
        ('Informations professionnelles', {
            'fields': ('numero_ordre', 'specialite', 'telephone')
        }),
        ('Statut', {
            'fields': ('statut', 'date_inscription', 'date_validation')
        }),
    )
    ordering = ('-date_inscription',)
    date_hierarchy = 'date_inscription'
    
    actions = ['valider_medecins', 'refuser_medecins']

    def save_model(self, request, obj, form, change):
        """
        Synchronise le statut du médecin avec l'utilisateur lié
        lorsque l'admin modifie le champ dans l'interface Django admin.
        """
        if change:
            previous = Medecin.objects.get(pk=obj.pk)
            statut_change = previous.statut != obj.statut
        else:
            statut_change = True

        if statut_change:
            if obj.statut == 'valide':
                obj.date_validation = timezone.now()
                if hasattr(obj.user, 'statut'):
                    obj.user.statut = 'verifie'
                    obj.user.save(update_fields=['statut'])
            elif obj.statut == 'refuse':
                if hasattr(obj.user, 'statut'):
                    obj.user.statut = 'exclu'
                    obj.user.save(update_fields=['statut'])
                obj.date_validation = None
            else:  # en_attente
                obj.date_validation = None
                if hasattr(obj.user, 'statut'):
                    obj.user.statut = 'en cours'
                    obj.user.save(update_fields=['statut'])

        super().save_model(request, obj, form, change)
    
    def valider_medecins(self, request, queryset):
        """Action pour valider plusieurs médecins"""
        count = 0
        for medecin in queryset.filter(statut='en_attente'):
            medecin.statut = 'valide'
            medecin.date_validation = timezone.now()
            medecin.save()
            if hasattr(medecin.user, 'statut'):
                medecin.user.statut = 'verifie'
                medecin.user.save(update_fields=['statut'])
            count += 1
        if count > 0:
            self.message_user(request, f'{count} médecin(s) validé(s) avec succès.', messages.SUCCESS)
        else:
            self.message_user(request, 'Aucun médecin en attente sélectionné.', messages.WARNING)
    valider_medecins.short_description = "Valider les médecins sélectionnés"
    
    def refuser_medecins(self, request, queryset):
        """Action pour refuser plusieurs médecins"""
        count = 0
        for medecin in queryset.filter(statut='en_attente'):
            medecin.statut = 'refuse'
            medecin.save()
            if hasattr(medecin.user, 'statut'):
                medecin.user.statut = 'exclu'
                medecin.user.save(update_fields=['statut'])
            count += 1
        if count > 0:
            self.message_user(request, f'{count} médecin(s) refusé(s).', messages.SUCCESS)
        else:
            self.message_user(request, 'Aucun médecin en attente sélectionné.', messages.WARNING)
    refuser_medecins.short_description = "Refuser les médecins sélectionnés"
