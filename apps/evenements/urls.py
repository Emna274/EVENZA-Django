from apps.core.routing import crud_urls

from .sections import SECTIONS
from .views import EventCreate, EventDetail, EventList, EventUpdate

app_name = "evenements"
urlpatterns = crud_urls(SECTIONS[0], listing=EventList, detail=EventDetail, create=EventCreate, update=EventUpdate)
