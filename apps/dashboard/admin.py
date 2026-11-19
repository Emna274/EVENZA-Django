from django.contrib import admin

from apps.core.admin import HistoryAdmin

from .models import Activity

admin.site.register(Activity, HistoryAdmin)
