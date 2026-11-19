from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.core.forms import StyledForm
from apps.utilisateurs.forms import AccountForm
from apps.utilisateurs.models import Role, User


class LoginForm(StyledForm, AuthenticationForm):
    username = forms.EmailField(label="Adresse e-mail", max_length=190,
                                widget=forms.EmailInput(attrs={"autocomplete": "username", "autofocus": True}))

    def clean_username(self):
        return self.cleaned_data["username"].lower()


class SignupForm(AccountForm):
    class Meta(AccountForm.Meta):
        fields = ("name", "email", "phone")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, actor=None, **kwargs)
        self.fields["password"].label = "Mot de passe"


class ProfileForm(StyledForm, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "phone", "availability", "skills")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.role != Role.ORGANIZER:
            self.fields.pop("availability")
            self.fields.pop("skills")
