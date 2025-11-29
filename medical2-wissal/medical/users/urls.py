from django.urls import path, include
from .views import PatientUpdateView
from .views import PatientDeleteView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/patient/', views.signup_patient, name='signup_patient'),
    path('signup/medecin/', views.signup_medecin, name='signup_medecin'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('acceuil/patient/', views.acceuil_patient, name='acceuil_patient'),
    path('acceuil/medecin/', views.acceuil_medecin, name='acceuil_medecin'),
    path('dashboard/home/', views.acceuil_admin, name='acceuil_admin'), 

    #path('dashboard/home/', views.dashboard_admin, name='acceuil_admin'),

    path('update/patient/', PatientUpdateView.as_view(), name='update_patient'),
    path('delete/patient/', PatientDeleteView.as_view(), name='delete_patient'),
    path('dashboard/patient/<int:pk>/archiver/', views.archiver_patient, name='archiver_patient'),
    path('dashboard/patient/<int:pk>/supprimer/', views.supprimer_patient, name='supprimer_patient'),
    path('dashboard/patient/<int:pk>/reactiver/', views.reactiver_patient, name='reactiver_patient'),
    path('specialites/', include('specialite.urls')), # gestion spécialités
    path('patient/liste_med/', views.liste_medecins, name='liste_medecins_patient'),
    #new
    path('dashboard-admin/', views.dashboard_admin, name='dashboard_admin'),

]
