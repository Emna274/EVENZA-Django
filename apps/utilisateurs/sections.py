from apps.core.sections import Module, Section

from .models import User


MODULE = Module("utilisateurs", "Utilisateurs", "Gestion des utilisateurs", "person-gear",
           "Gérez les comptes, les rôles et les accès de votre équipe.")
SECTIONS = (
    Section("users", "utilisateurs", "", "Utilisateurs", User,
            "name email phone role is_active availability skills", "name email role is_active", "name email skills", "role"),
)
