from django.contrib.auth import views as auth
from django.urls import path, reverse_lazy

from . import views

urlpatterns = [
    path("connexion/", views.SignIn.as_view(), name="login"),
    path("inscription/", views.Signup.as_view(), name="signup"),
    path("deconnexion/", auth.LogoutView.as_view(), name="logout"),
    path("parametres/", views.Profile.as_view(), name="profile"),
    path("parametres/mot-de-passe/", auth.PasswordChangeView.as_view(
        template_name="registration/form.html", success_url=reverse_lazy("password_change_done"),
        extra_context={"title": "Changer le mot de passe", "submit_label": "Enregistrer"}), name="password_change"),
    path("parametres/mot-de-passe/confirme/", auth.PasswordChangeDoneView.as_view(
        template_name="registration/status.html", extra_context={"title": "Mot de passe mis à jour"}),
        name="password_change_done"),
    path("recuperation/", auth.PasswordResetView.as_view(
        template_name="registration/form.html", email_template_name="registration/password_reset_email.txt",
        subject_template_name="registration/password_reset_subject.txt",
        extra_context={"title": "Récupérer mon accès", "submit_label": "Envoyer le lien"}), name="password_reset"),
    path("recuperation/envoyee/", auth.PasswordResetDoneView.as_view(
        template_name="registration/status.html",
        extra_context={"title": "Consultez votre messagerie",
                       "description": "Si un compte actif correspond à cette adresse, un lien de réinitialisation vous est envoyé."}),
        name="password_reset_done"),
    path("recuperation/<uidb64>/<token>/", auth.PasswordResetConfirmView.as_view(
        template_name="registration/form.html",
        extra_context={"title": "Définir un mot de passe", "submit_label": "Enregistrer"}), name="password_reset_confirm"),
    path("recuperation/terminee/", auth.PasswordResetCompleteView.as_view(
        template_name="registration/status.html", extra_context={"title": "Mot de passe réinitialisé"}),
        name="password_reset_complete"),
    path("notifications/", views.Notifications.as_view(), name="notifications"),
]
