from apps.core.routing import crud_urls

from .sections import SECTIONS
from .views import ProgramCreate, ProgramList, ProgramUpdate, SuggestionDetail

app_name = "programmes"
program, suggestion = SECTIONS
urlpatterns = [
    *crud_urls(program, listing=ProgramList, create=ProgramCreate, update=ProgramUpdate),
    *crud_urls(suggestion, listing=ProgramList, detail=SuggestionDetail, create=ProgramCreate, update=ProgramUpdate),
]
