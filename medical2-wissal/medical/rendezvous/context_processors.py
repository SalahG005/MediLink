from .models import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread = notifs.filter(is_read=False).count()
        return {
            'global_notifications': notifs,
            'global_unread_count': unread
        }
    return {}
