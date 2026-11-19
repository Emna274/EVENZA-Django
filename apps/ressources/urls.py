from apps.core.routing import crud_urls

from .sections import SECTIONS
from .views import AllocationList, ResourceCreate, ResourceDetail, ResourceList, ResourceUpdate

app_name = "ressources"
resource, allocation = SECTIONS
urlpatterns = [
    *crud_urls(resource, listing=ResourceList, detail=ResourceDetail, create=ResourceCreate, update=ResourceUpdate),
    *crud_urls(allocation, listing=AllocationList, create=ResourceCreate, update=ResourceUpdate),
]
