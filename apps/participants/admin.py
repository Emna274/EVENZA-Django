from django.contrib import admin

from apps.core.admin import HistoryAdmin, register_sections

from .models import Document
from .sections import SECTIONS

register_sections(SECTIONS)


@admin.register(Document)
class DocumentAdmin(HistoryAdmin):
    exclude = ("content",)
