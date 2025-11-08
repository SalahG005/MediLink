from django.urls import path
from .views import PatientUpdateView
from .views import PatientDeleteView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/patient/', views.signup_patient, name='signup_patient'),
    path('signup/medecin/', views.signup_medecin, name='signup_medecin'),
    path('signin/', views.signin, name='signin'),
    path('acceuil/patient/', views.acceuil_patient, name='acceuil_patient'),
    path('acceuil/medecin/', views.acceuil_medecin, name='acceuil_medecin'),
    path('update/patient/', PatientUpdateView.as_view(), name='update_patient'),
     path('delete/patient/', PatientDeleteView.as_view(), name='delete_patient'),
]
