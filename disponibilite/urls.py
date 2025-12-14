from django.urls import path
from .views import CalendarView, DisponibiliteJson, DisponibiliteAdd, DisponibiliteDelete, DisponibiliteUpdate,DisponibiliteJson

app_name = 'disponibilite'

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),
    path('json/', DisponibiliteJson.as_view(), name='disponibilite_json'),
    path('add/', DisponibiliteAdd.as_view(), name='disponibilite_add'),
    path('delete/<int:dispo_id>/', DisponibiliteDelete.as_view(), name='disponibilite_delete'),
    path('update/<int:dispo_id>/', DisponibiliteUpdate.as_view(), name='disponibilite_update'),
    path('json/', DisponibiliteJson.as_view(), name='json_disponibilites'),

]
