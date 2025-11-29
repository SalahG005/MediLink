from django.contrib import admin
from .models import TimeSlot, RendezVous

# Makes TimeSlot appear in admin dashboard
@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_available')
    ordering = ('date',)
    list_filter = ('is_available',)

# Makes RendezVous appear in admin dashboard
@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('patient', 'slot', 'status', 'booked_at')
    list_filter = ('status',)
    search_fields = ('patient__username',)
