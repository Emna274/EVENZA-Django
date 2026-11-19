from django.urls import path

from apps.core.routing import crud_urls

from . import views
from .sections import SECTIONS

app_name = "participants"
participant, complaint = SECTIONS
urlpatterns = [
    *crud_urls(participant, detail=views.ParticipantDetail, create=views.ParticipantCreate, update=views.ParticipantUpdate),
    *crud_urls(complaint, create=views.ComplaintCreate, update=views.ComplaintUpdate),
]

# Ces noms sont publics et historiquement résolus sans namespace.
public_urlpatterns = [
    path("invitations/<str:token>/", views.invitation, name="invitation"),
    path("participants/<int:pk>/badge/", views.badge, name="badge"),
    path("participants/presence/<str:token>/", views.check_in, name="check-in"),
    path("participants/<int:pk>/documents/ajouter/", views.upload_document, name="upload-document"),
    path("documents/<int:pk>/", views.download_document, name="download-document"),
    path("documents/<int:pk>/supprimer/", views.delete_document, name="delete-document"),
]
