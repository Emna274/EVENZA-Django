import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.core.access import SECTIONS, allowed, is_admin, scoped
from apps.core.audit import record_activity, record_changes
from apps.core.views import RecordCreate, RecordDetail, RecordUpdate
from apps.evenements.models import Event
from apps.utilisateurs.models import Role

from .forms import DocumentForm, record_form
from .models import Document, Participant
from .operations import complaint_status_changed, participant_status_changed


class ParticipantDetail(RecordDetail):
    template_name = "participants/detail.html"
    related_sections = (("complaints", "participant"),)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, record = self.request.user, self.object
        context["documents"] = record.documents.defer("content")
        context["document_form"] = DocumentForm()
        context["can_upload"] = is_admin(user) or user.role == Role.ORGANIZER or record.user_id == user.pk
        if record.status in Participant.BADGE_STATUSES and record.event.status != Event.Status.CANCELLED:
            context["badge_url"] = reverse("badge", args=[record.pk])
        return context


class ParticipantEditor:
    record_form = staticmethod(record_form)
    status_changed = staticmethod(participant_status_changed)


class ParticipantCreate(ParticipantEditor, RecordCreate):
    pass


class ParticipantUpdate(ParticipantEditor, RecordUpdate):
    pass


class ComplaintEditor:
    record_form = staticmethod(record_form)
    status_changed = staticmethod(complaint_status_changed)


class ComplaintCreate(ComplaintEditor, RecordCreate):
    pass


class ComplaintUpdate(ComplaintEditor, RecordUpdate):
    pass


@login_required
@transaction.atomic
def invitation(request, token):
    from django.core import signing
    from django.http import Http404

    try:
        data = signing.loads(token, salt="evenza-invitation", max_age=30 * 86400)
    except signing.BadSignature as error:
        raise Http404 from error
    if request.user.role != Role.PARTICIPANT or request.user.email != data["email"]:
        raise PermissionDenied
    record = get_object_or_404(Participant, pk=data["pk"], email=data["email"])
    if record.user_id and record.user_id != request.user.pk:
        raise PermissionDenied
    if request.method == "POST":
        response = request.POST.get("response")
        if (response not in {"confirm", "decline"} or record.status != Participant.Status.INVITED or
                record.event.start_at <= timezone.now() or record.event.status == Event.Status.CANCELLED):
            raise PermissionDenied
        record.user = request.user
        record.status = Participant.Status.CONFIRMED if response == "confirm" else Participant.Status.DECLINED
        if response == "confirm" and record.event.registrations.filter(
                status__in=Participant.OCCUPIED).count() >= record.event.capacity:
            record.status = Participant.Status.WAITLIST
        try:
            record.full_clean()
            record.save(update_fields=["user", "status"])
        except ValidationError as error:
            messages.error(request, " ".join(error.messages))
        else:
            record_changes(request.user, SECTIONS["participants"], record, "Réponse à l’invitation",
                           Participant.Status.INVITED, participant_status_changed)
            messages.success(request, "Votre réponse a été enregistrée.")
            return redirect(SECTIONS["participants"].url("detail", record.pk))
    return render(request, "participants/invitation.html", {"title": "Invitation", "record": record})


@login_required
def badge(request, pk):
    import qrcode
    from qrcode.image.svg import SvgPathImage

    record = get_object_or_404(scoped(request.user, SECTIONS["participants"]),
                               pk=pk, status__in=Participant.BADGE_STATUSES)
    if record.event.status == Event.Status.CANCELLED:
        raise PermissionDenied
    url = request.build_absolute_uri(reverse("check-in", args=[record.badge_token]))
    image = qrcode.make(url, image_factory=SvgPathImage)
    return HttpResponse(image.to_string(), content_type="image/svg+xml",
                        headers={"Cache-Control": "private, no-store"})


@login_required
@transaction.atomic
def check_in(request, token):
    section = SECTIONS["participants"]
    if request.method not in {"GET", "POST", "HEAD"}:
        return HttpResponse(status=405, headers={"Allow": "GET, HEAD, POST"})
    if not allowed(request.user, section, "change") or request.user.role == Role.PARTICIPANT:
        raise PermissionDenied
    record = get_object_or_404(scoped(request.user, section), badge_token=token,
                               status__in=Participant.BADGE_STATUSES)
    if record.event.status == Event.Status.CANCELLED:
        raise PermissionDenied
    if request.method == "POST":
        previous = record.status
        if previous != Participant.Status.PRESENT:
            record.status = Participant.Status.PRESENT
            record.save(update_fields=["status"])
            record_changes(request.user, section, record, "Pointage QR", previous, participant_status_changed)
        messages.success(request, "La présence est enregistrée.")
        return redirect(section.url("detail", record.pk))
    return render(request, "participants/check_in.html", {"title": "Contrôler un badge", "record": record})


def private_document(user, pk):
    participants = scoped(user, SECTIONS["participants"])
    return get_object_or_404(Document, pk=pk, participant__in=participants)


@login_required
@require_POST
@transaction.atomic
def upload_document(request, pk):
    section = SECTIONS["participants"]
    record = get_object_or_404(scoped(request.user, section), pk=pk)
    form = DocumentForm(request.POST, request.FILES)
    if form.is_valid():
        file = form.cleaned_data["document"]
        Document.objects.create(participant=record, original_name=file.name,
                                       mime=form.mime, size=file.size, content=file.read())
        record_activity(request.user, section, pk, "Dépôt d’un document")
        messages.success(request, "Le document a été ajouté.")
    else:
        messages.error(request, " ".join(error for errors in form.errors.values() for error in errors))
    return redirect(section.url("detail", pk))


@login_required
def download_document(request, pk):
    from django.http import FileResponse

    document = private_document(request.user, pk)
    return FileResponse(io.BytesIO(document.content), as_attachment=True, filename=document.original_name,
                        content_type=document.mime, headers={"Cache-Control": "private, no-store",
                                                             "X-Content-Type-Options": "nosniff"})


@login_required
@require_POST
@transaction.atomic
def delete_document(request, pk):
    document = private_document(request.user, pk)
    participant_id = document.participant_id
    document.delete()
    record_activity(request.user, SECTIONS["participants"], participant_id, "Suppression d’un document")
    messages.success(request, "Le document a été supprimé.")
    return redirect(SECTIONS["participants"].url("detail", participant_id))
