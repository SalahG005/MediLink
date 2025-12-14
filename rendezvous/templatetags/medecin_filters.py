# rendezvous/templatetags/medecin_filters.py
from django import template
register = template.Library()

@register.filter
def get_medecin_id(medecins, full_name):
    for m in medecins:
        if m.get_full_name.lower() == full_name.lower():
            return m.id
    return 0
