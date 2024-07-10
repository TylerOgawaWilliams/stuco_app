from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    UsernameField,
)
from django.forms.widgets import EmailInput
from users.models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Specify the user model created while adding a user
    on the admin page.
    """

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        ]


class CustomUserChangeForm(UserChangeForm):
    """
    Specify the user model edited while editing a user on the
    admin page.
    """

    class Meta:
        model = CustomUser
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "password",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        ]


class CustomAdminAuthenticationForm(AuthenticationForm):
    username = UsernameField(widget=EmailInput(attrs={"autofocus": True}))
