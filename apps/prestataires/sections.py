from apps.core.sections import Module, Section

from .models import Provider, Reservation, Service


MODULE = Module("prestataires", "Prestataires", "Gestion des prestataires", "briefcase",
           "Retrouvez vos partenaires, leurs services et vos réservations.")
SECTIONS = (
    Section("providers", "prestataires", "", "Prestataires", Provider,
            "name specialty city email phone availability user status", "name specialty city email status",
            "name specialty city email availability"),
    Section("services", "prestataires", "services/", "Services", Service,
            "provider name description price status", "name provider price status", "name provider__name description"),
    Section("reservations", "prestataires", "reservations/", "Réservations", Reservation,
            "event service amount status rating comment", "service event amount status rating",
            "event__title service__name service__provider__name"),
)
