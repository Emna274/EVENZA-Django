from django.contrib import admin
from django.urls import include, path

from apps.core.admin_urls import legacy_model_urls
from apps.core.operations import record_operation
from apps.participants.urls import public_urlpatterns


admin_patterns, admin_app_name, admin_namespace = admin.site.urls

urlpatterns = [
    path("", include("apps.dashboard.urls")),
    path("", include("apps.accounts.urls")),
    path("actions/<slug:key>/<int:pk>/<slug:operation>/", record_operation, name="record-operation"),
    path("", include(public_urlpatterns)),
    path("admin/", include(([*legacy_model_urls(admin.site), *admin_patterns], admin_app_name), admin_namespace)),
    path("evenements/", include("apps.evenements.urls")),
    path("prestataires/", include("apps.prestataires.urls")),
    path("utilisateurs/", include("apps.utilisateurs.urls")),
    path("programmes/", include("apps.programmes.urls")),
    path("participants/", include("apps.participants.urls")),
    path("ressources/", include("apps.ressources.urls")),
]
