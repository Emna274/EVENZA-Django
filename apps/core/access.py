from functools import reduce
from operator import or_

from django.db.models import Q

from apps.evenements import sections as evenements
from apps.prestataires import sections as prestataires
from apps.utilisateurs import sections as utilisateurs
from apps.programmes import sections as programmes
from apps.participants import sections as participants
from apps.ressources import sections as ressources
from apps.evenements.models import Event
from apps.participants.models import Participant
from apps.prestataires.models import Reservation
from apps.utilisateurs.models import Role

DOMAINS = (evenements, prestataires, utilisateurs, programmes, participants, ressources)
MODULES = {domain.MODULE.slug: domain.MODULE for domain in DOMAINS}
SECTIONS = {section.key: section for domain in DOMAINS for section in domain.SECTIONS}
BY_MODEL = {section.model: section for section in SECTIONS.values()}

ORGANIZER_WRITE = {"events", "programs", "suggestions", "participants", "complaints",
                   "resources", "allocations", "reservations"}
PROVIDER_READ = {"providers", "services", "reservations", "events", "programs"}
CLIENT_READ = {"events", "programs"}
PARTICIPANT_READ = {"events", "programs", "participants", "complaints"}


def is_admin(user):
    return user.is_superuser or user.role == Role.ADMIN


def allowed(user, section, action="view"):
    if not user.is_authenticated or not user.is_active:
        return False
    if is_admin(user):
        return True

    key = section.key
    role = user.role
    if action == "view":
        return {
            Role.ORGANIZER: key != "users",
            Role.PROVIDER: key in PROVIDER_READ,
            Role.CLIENT: key in CLIENT_READ,
            Role.PARTICIPANT: key in PARTICIPANT_READ,
        }.get(role, False)
    if role == Role.ORGANIZER:
        return key in ORGANIZER_WRITE
    if role == Role.PROVIDER:
        return key == "services" or (key in {"providers", "reservations"} and action == "change")
    if role == Role.CLIENT:
        return key == "events" and action == "add"
    return (key == "participants" and action in {"add", "change"}) or (key == "complaints" and action == "add")


def scoped(user, section):
    queryset = section.model.objects.all()
    if not allowed(user, section):
        return queryset.none()
    if is_admin(user):
        return queryset

    key = section.key
    if user.role == Role.ORGANIZER:
        event = Q(organizer=user)
        related = Q(event__organizer=user)
        scopes = {"events": event, "programs": related, "reservations": related, "suggestions": related,
                  "participants": related, "allocations": related, "complaints": Q(participant__event__organizer=user)}
    elif user.role == Role.PROVIDER:
        own_events = Reservation.objects.filter(service__provider__user=user).values("event")
        scopes = {"providers": Q(user=user), "services": Q(provider__user=user),
                  "reservations": Q(service__provider__user=user), "events": Q(pk__in=own_events),
                  "programs": Q(event__in=own_events)}
    elif user.role == Role.CLIENT:
        scopes = {"events": Q(client=user), "programs": Q(event__client=user)}
    else:
        registrations = Participant.objects.filter(user=user).values("event")
        visible = Q(status=Event.Status.CONFIRMED) | Q(pk__in=registrations)
        scopes = {"events": visible, "programs": Q(event__status=Event.Status.CONFIRMED) | Q(event__in=registrations),
                  "participants": Q(user=user), "complaints": Q(participant__user=user)}
    return queryset.filter(scopes.get(key, Q()))


def search_query(query, fields):
    return reduce(or_, (Q(**{f"{field}__icontains": query}) for field in fields.split()))
