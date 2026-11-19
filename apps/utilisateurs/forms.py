from django import forms
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from apps.core.forms import RecordForm

from .models import User


class AccountForm(RecordForm):
    password = forms.CharField(label="Nouveau mot de passe", required=False, max_length=200,
                               strip=False, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    class Meta:
        model = User
        fields = ("name", "email", "phone", "role", "is_active", "availability", "skills")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].required = not self.instance.pk
        if self.instance.pk:
            self.fields["password"].help_text = "Laissez ce champ vide pour conserver le mot de passe actuel."
        if self.actor and self.instance.pk == self.actor.pk:
            self.fields["role"].disabled = self.fields["is_active"].disabled = True

    def clean(self):
        data = super().clean()
        password = data.get("password")
        if password:
            user = User(email=data.get("email", ""), name=data.get("name", ""))
            try:
                password_validation.validate_password(password, user)
            except ValidationError as error:
                self.add_error("password", error)
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            self.save_m2m()
        return user
