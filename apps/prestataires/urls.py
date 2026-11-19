from apps.core.routing import crud_urls

from .sections import SECTIONS
from .views import ProviderCreate, ProviderDetail, ProviderList, ProviderUpdate, ReservationCreate, ReservationUpdate

app_name = "prestataires"
provider, service, reservation = SECTIONS
urlpatterns = [
    *crud_urls(provider, listing=ProviderList, detail=ProviderDetail, create=ProviderCreate, update=ProviderUpdate),
    *crud_urls(service),
    *crud_urls(reservation, create=ReservationCreate, update=ReservationUpdate),
]
