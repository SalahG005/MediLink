from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('medecin/', views.dashboard_medecin, name='dashboard_medecin'),
]
