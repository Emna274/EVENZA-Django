from django.contrib import admin


def register_sections(sections):
    for section in sections:
        options = {
            "list_display": tuple(section.columns.split()),
            "list_filter": (section.filter,),
            "search_fields": tuple(section.search.split()),
            "list_select_related": True,
        }
        admin.site.register(section.model, type(f"{section.model.__name__}Admin", (admin.ModelAdmin,), options))


class HistoryAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
