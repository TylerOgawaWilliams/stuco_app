from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    UsernameField,
)
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.forms.widgets import EmailInput
from django import forms
from users.models import CustomUser
import re

import logging


LOGGER = logging.getLogger(__name__)

VALID_PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%]).{8,24}$"


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

    def clean_email(self):
        LOGGER.warning(f"In Clean Email: {self.cleaned_data}")
        email = self.cleaned_data.get("email")
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValidationError(f"Invalid email format {str(e)}")
        return email.lower()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email:
            cleaned_data["email"] = email.lower()
        else:
            self.add_error("email", "Valid Email is required.")
        return cleaned_data


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


class CustomUserRegisterForm(CustomUserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "middle_name", "last_name", "email", "password1", "password2"]

    def clean_email(self):
        LOGGER.warning(f"In Clean Email: {self.cleaned_data}")
        email = super().clean_email()
        # Make sure this user doesn't already exist
        LOGGER.warning(f"Checking for existing user with email: {email}")
        try:
            _ = CustomUser.objects.get(email=email)
            raise ValidationError(f"User with email {email} already exists.")
        except CustomUser.DoesNotExist:
            LOGGER.warning(f"User with email {email} does not exist. Continuing . . .")
            pass
        except ValidationError as e:
            raise ValidationError(f"Invalid email format {str(e)}")
        return email.lower()


class ConfirmEmailForm(forms.Form):
    confirmation_code = forms.CharField(
        label="Confirmation Code",
        max_length=7,
        help_text="Enter the confirmation code sent to your email address",
    )
    email = forms.EmailField(
        label="Email",
        help_text="Enter the email address that you used to register",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email:
            cleaned_data["email"] = email.lower()
        else:
            self.add_error("email", "Valid Email is required.")

        confirmation_code = cleaned_data.get("confirmation_code")
        if not confirmation_code:
            self.add_error("confirmation_code", "Confirmation Code is required.")
        else:
            target_user = CustomUser.objects.filter(email=email).first()
            if not target_user or (confirmation_code != target_user.confirmation_code):
                self.add_error("email", "Email Address and Confirmation Code do not match.")
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        help_text="Enter the email address that you used to register",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email:
            cleaned_data["email"] = email.lower()
        else:
            self.add_error("email", "Valid Email is required.")
        target_user = CustomUser.objects.filter(email=email).first()
        if not target_user:
            self.add_error("email", "Sorry, we do not recognize that email address.  Want to try another?")
        return cleaned_data


class ResetPasswordForm(forms.Form):
    confirmation_code = forms.CharField(
        label="Confirmation Code",
        max_length=7,
        help_text="Enter the confirmation code sent to your email address",
    )
    email = forms.EmailField(
        label="Email",
        help_text="Enter the email address that you used to register",
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(render_value=True),
        help_text="Enter a new password",
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(render_value=True),
        help_text="Confirm your new password",
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        if email:
            cleaned_data["email"] = email.lower()
        else:
            self.add_error("email", "Valid Email is required.")
        target_user = CustomUser.objects.filter(email=email).first()
        if not target_user or (cleaned_data.get("confirmation_code") != target_user.confirmation_code):
            self.add_error(
                "email",
                "Invalid email address and confirmation code combination.  Please consult the email that "
                "was sent to you",
            )
        password = cleaned_data.get("password1")
        LOGGER.warning(f"Validation Password: {password}")
        try:
            validate_password(password, target_user)
        except ValidationError as e:
            for next_error in e.error_list:
                self.add_error("password1", next_error)
        if not re.match(VALID_PASSWORD_REGEX, password):
            self.add_error(
                "password1",
                "Password must be between 8 and 24 characters, contain at least one uppercase letter, one lowercase "
                "letter, one number, and one special character.",
            )
        cleaned_data["password1"] = password
        password_confirm = cleaned_data.get("password2")
        if password != password_confirm:
            self.add_error("password2", "Passwords do not match.")

        LOGGER.warning(f"Cleansed Data: {cleaned_data}")

        return cleaned_data
