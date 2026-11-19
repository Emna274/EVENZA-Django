from django.urls import path

from .views import RecordCreate, RecordDelete, RecordDetail, RecordList, RecordUpdate


def crud_urls(section, *, listing=RecordList, create=RecordCreate, detail=RecordDetail,
              update=RecordUpdate, delete=RecordDelete):
    routes = (
        ("list", "", listing),
        ("create", "ajouter/", create),
        ("detail", "<int:pk>/", detail),
        ("update", "<int:pk>/modifier/", update),
        ("delete", "<int:pk>/supprimer/", delete),
    )
    return [
        path(section.path + suffix, view.as_view(section=section), name=f"{section.key}-{action}")
        for action, suffix, view in routes
    ]
