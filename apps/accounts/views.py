from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, UpdateView

from .forms import LoginForm, ProfileForm, SignupForm
from .models import LoginAlert, LoginAttempt


class SignIn(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        from ipaddress import ip_address

        email = request.POST.get("username", "").strip().lower()[:190]
        try:
            ip = str(ip_address(request.META.get("REMOTE_ADDR", "")))
        except ValueError:
            ip = None
        criteria = Q(email=email)
        if ip:
            criteria |= Q(ip=ip)
        failures = LoginAttempt.objects.filter(criteria, success=False,
                                                       created_at__gte=timezone.now() - timedelta(minutes=15))
        failed_count = failures.count()
        if failed_count >= 10:
            form = self.get_form()
            form.add_error(None, "Trop de tentatives. Réessayez dans 15 minutes.")
            return self.render_to_response(self.get_context_data(form=form), status=429)
        response = super().post(request, *args, **kwargs)
        LoginAttempt.objects.create(email=email, ip=ip, success=request.user.is_authenticated)
        if not request.user.is_authenticated and failed_count == 4:
            LoginAlert.objects.create(email=email, ip=ip)
        return response


class Signup(CreateView):
    form_class = SignupForm
    template_name = "registration/form.html"
    success_url = reverse_lazy("login")
    extra_context = {"title": "Créer un compte", "submit_label": "S’inscrire"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre compte a été créé. Vous pouvez vous connecter.")
        return response


class Profile(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("profile")
    extra_context = {"title": "Paramètres"}

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Votre profil a été mis à jour.")
        return response


class Notifications(LoginRequiredMixin, ListView):
    template_name = "accounts/notifications.html"
    extra_context = {"title": "Notifications"}
    paginate_by = 15

    def get_queryset(self):
        return self.request.user.notifications.all()

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(read_at=None)
        if "notification" in request.POST:
            value = request.POST["notification"]
            if not value.isascii() or not value.isdecimal() or len(value) > 18:
                raise PermissionDenied
            queryset = queryset.filter(pk=int(value))
        queryset.update(read_at=timezone.now())
        return redirect("notifications")
