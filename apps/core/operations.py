from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.participants import operations as participants
from apps.prestataires import operations as prestataires
from apps.programmes import operations as programmes

from .access import SECTIONS, allowed, scoped


OPERATIONS = {
    "suggestions": programmes,
    "reservations": prestataires,
    "participants": participants,
}


def available_operations(user, section, record):
    module = OPERATIONS.get(section.key)
    if not module or not allowed(user, section, "change"):
        return []
    return [(action, label, reverse("record-operation", args=[section.key, record.pk, action]))
            for action, label in module.choices(user, record)]


@login_required
@require_POST
@transaction.atomic
def record_operation(request, key, pk, operation):
    section = SECTIONS.get(key)
    if section is None or not allowed(request.user, section, "change"):
        raise PermissionDenied
    record = get_object_or_404(scoped(request.user, section), pk=pk)
    if operation not in {action for action, _, _ in available_operations(request.user, section, record)}:
        raise PermissionDenied
    try:
        OPERATIONS[key].perform(request, record, operation)
    except ValidationError as error:
        messages.error(request, " ".join(error.messages))
    except OSError:
        messages.error(request, "Le service de messagerie est indisponible.")
    return redirect(section.url("detail", pk))
