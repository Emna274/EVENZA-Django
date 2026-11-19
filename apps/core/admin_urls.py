from django.apps import apps
from django.contrib.admin.sites import NotRegistered
from django.urls import include, path


def legacy_model_urls(site):
    """Conserve les URL et les noms des anciennes pages d’administration."""
    patterns = []
    for model in apps.get_models():
        opts = model._meta
        if opts.app_label == "gestion" or opts.db_table != f"gestion_{opts.model_name}":
            continue
        try:
            model_admin = site.get_model_admin(model)
        except NotRegistered:
            continue
        prefix = f"{opts.app_label}_{opts.model_name}_"
        aliases = [
            path(str(route.pattern), route.callback, kwargs=route.default_args,
                 name=route.name.replace(prefix, f"gestion_{opts.model_name}_", 1) if route.name else None)
            for route in model_admin.urls
        ]
        patterns.append(path(f"gestion/{opts.model_name}/", include(aliases)))
    return patterns
