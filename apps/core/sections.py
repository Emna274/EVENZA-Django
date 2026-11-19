from dataclasses import dataclass

from django.urls import reverse


@dataclass(frozen=True)
class Module:
    slug: str
    label: str
    title: str
    icon: str
    description: str


@dataclass(frozen=True)
class Section:
    key: str
    module: str
    path: str
    label: str
    model: type
    fields: str
    columns: str
    search: str
    filter: str = "status"

    def url(self, action="list", pk=None):
        return reverse(f"{self.module}:{self.key}-{action}", args=() if pk is None else (pk,))
