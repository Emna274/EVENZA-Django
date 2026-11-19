from django.contrib import admin

from apps.core.admin import HistoryAdmin

from .models import LoginAlert, LoginAttempt, Notification

admin.site.register([LoginAttempt, Notification], HistoryAdmin)


@admin.register(LoginAlert)
class LoginAlertAdmin(HistoryAdmin):
    list_display = ("email", "ip", "created_at")
    search_fields = ("email", "ip")
