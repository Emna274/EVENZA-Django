from apps.core.routing import crud_urls

from .sections import SECTIONS
from .views import UserCreate, UserDelete, UserDetail, UserList, UserUpdate

app_name = "utilisateurs"
urlpatterns = crud_urls(
    SECTIONS[0], listing=UserList, detail=UserDetail, create=UserCreate, update=UserUpdate, delete=UserDelete,
)
