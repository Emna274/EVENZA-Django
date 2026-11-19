from apps.core.sections import Module, Section

from .models import Allocation, Resource


MODULE = Module("ressources", "Ressources", "Gestion des ressources", "boxes",
           "Suivez votre inventaire et anticipez les besoins en matériel.")
SECTIONS = (
    Section("resources", "ressources", "", "Ressources", Resource,
            "name category quantity status description", "name category quantity status", "name description"),
    Section("allocations", "ressources", "affectations/", "Affectations", Allocation,
            "event resource quantity start_at end_at status", "resource event quantity start_at status",
            "resource__name event__title"),
)
