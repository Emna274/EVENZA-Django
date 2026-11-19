from .access import MODULES, SECTIONS, allowed


def navigation(request):
    sections = [section for section in SECTIONS.values() if not section.path and allowed(request.user, section)]
    return {
        "navigation": [(MODULES[section.module], section.url()) for section in sections],
        "unread_notifications": (request.user.notifications.filter(read_at__isnull=True).count()
                                 if request.user.is_authenticated else 0),
    }
