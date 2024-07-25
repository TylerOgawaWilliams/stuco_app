# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserRegisterForm, ConfirmEmailForm, ForgotPasswordForm, ResetPasswordForm
from .models import CustomUser
from django.conf import settings
from core.services.cognito_idp_service import cognito_client, PasswordDoesNotMeetCriteriaException
from core.services.email_service import MailSender
import core.util as util
import logging
from django.http import HttpResponseBadRequest
import random
import string

LOGGER = logging.getLogger(__name__)


def generate_random_confirmation_code():
    # using random.choices()
    # generating random strings
    res = "".join(random.choices(string.digits, k=settings.CONFIRMATION_CODE_LENGTH))
    return str(res)


def sign_up(request):
    if request.method == "GET":
        form = CustomUserRegisterForm()
        return render(request, "users/register.html", {"form": form})

    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            site_url_base = util.get_system_base_url(request)
            create_new_user(user, site_url_base=site_url_base)
            messages.success(
                request,
                "You have successfully registered.  Please confirm your email "
                "address with the confirmation code sent to the email address that you supplied.",
            )
            return redirect("confirm_email")
        else:
            return render(request, "users/register.html", {"form": form})


def confirm_email(request):
    if request.method == "GET":
        form = ConfirmEmailForm(initial={"confirmation_code": request.GET.get("confirmation_code", None)})

        return render(request, "users/confirm_email.html", {"form": form})

    if request.method == "POST":
        form = ConfirmEmailForm(request.POST)
        if form.is_valid():
            # Validation checked that the email and confirmation code are valid
            # We just need to update the user now to be active and clear out the
            # confirmation code
            try:
                user = CustomUser.objects.get(email=form.cleaned_data["email"])
                if settings.USE_COGNITO:
                    cognito_client().admin_confirm_sign_up(
                        form.cleaned_data["email"],
                    )
                user.confirmation_code = None
                user.is_active = True
                user.save()
                messages.success(request, f"Email Address {user.email} has been confirmed.  You may now login.")
                return redirect("login")
            except Exception:
                LOGGER.exception("Unable to confirm email address for user")
                messages.error(request, "Unable to confirm email address.  Please contact support.")
                return render(request, "users/confirm_email.html", {"form": form})

        else:
            return render(request, "users/confirm_email.html", {"form": form})


def forgot_password(request):
    if request.method == "GET":
        form = ForgotPasswordForm()
        return render(request, "users/forgot_password.html", {"form": form})

    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # First, we need to create a random confirmation code and add that to the user
            # so that we can confirm the user's email address later
            user = CustomUser.objects.get(email=form.cleaned_data["email"])
            user.confirmation_code = generate_random_confirmation_code()

            # Now we need to save the user
            user.save()

            # # Now we need to send the confirmation code to the user
            site_url_base = util.get_system_base_url(request)
            mail_sender = MailSender()
            mail_sender.send_password_reset_confirm_email(
                from_email=settings.SYSTEM_EMAIL_SENDER,
                recipients_list=user.email,
                confirmation_code=user.confirmation_code,
                webapp_base_url=site_url_base,
                first_name=user.first_name,
            )

            messages.success(
                request,
                "Check your email for password reset instructions.",
            )
            return redirect("reset_password")
        else:
            return render(request, "users/forgot_password.html", {"form": form})


def reset_password(request):
    if request.method == "GET":
        form = ResetPasswordForm(initial={"confirmation_code": request.GET.get("confirmation_code", None)})

        return render(request, "users/reset_password.html", {"form": form})

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Validation checked that the email and confirmation code are valid
            # We just need to update the user now to be active and clear out the
            # confirmation code
            try:
                user = CustomUser.objects.get(email=form.cleaned_data["email"])
                if settings.USE_COGNITO:
                    cognito_client().reset_password(
                        form.cleaned_data["email"],
                        form.cleaned_data["confirmation_code"],
                        form.cleaned_data["password1"],
                    )
                else:
                    user.set_password(form.cleaned_data["password1"])

                user.confirmation_code = None
                user.is_active = True
                user.save()

                # Now we need to send the confirmation code to the user
                mail_sender = MailSender()
                mail_sender.send_password_reset_success_email(
                    from_email=settings.SYSTEM_EMAIL_SENDER,
                    recipients_list=user.email,
                    first_name=user.first_name,
                )

                messages.success(request, f"Password has been reset for {user.email}.")

                return redirect("login")
            except Exception:
                LOGGER.exception("Unable to reset password for user")
                messages.error(request, "Unable to reset password.  Please contact support.")
                return render(request, "users/reset_password.html", {"form": form})
        else:
            messages.error(request, "Please correct the errors below")
            return render(request, "users/reset_password.html", {"form": form})


def create_new_user(user: CustomUser, site_url_base: str = None) -> CustomUser:
    # For security reasons, we do not allow super users to get created via the api
    # so regardless of the value that is sent in for is_superuser, we will set it to False
    user.is_superuser = False

    if settings.USE_COGNITO:
        # First we must create a Cognito User
        try:
            cognito_client().sign_up_user(user.email, user.password)
        except PasswordDoesNotMeetCriteriaException as e:
            LOGGER.exception(f"Error creating Cognito User: {user.email}")
            raise HttpResponseBadRequest(
                status_code=400,
                detail=str(e),
            )
        except Exception as e:
            if "User already exists" in str(e):
                LOGGER.warning(f"User {user.email} already exists in Cognito. Continuing . . . ")
            else:
                LOGGER.exception(f"Error creating Cognito User: {user.email}")
                raise HttpResponseBadRequest(
                    status_code=400,
                    detail="Error creating Cognito User",
                )

    # if we got this far, there is a Cognito User (or we are using local users) so the user will be able
    # to login with the password they provided
    # Now we need to create a local user record if one does not already exist

    # First, we need to create a random confirmation code and add that to the user
    # so that we can confirm the user's email address later
    user.confirmation_code = generate_random_confirmation_code()
    user.is_active = False

    # Now we need to save the user
    user.save()

    # # Now we need to send the confirmation code to the user
    mail_sender = MailSender()
    mail_sender.send_app_registration_email(
        from_email=settings.SYSTEM_EMAIL_SENDER,
        recipients_list=user.email,
        confirmation_code=user.confirmation_code,
        webapp_base_url=site_url_base,
    )

    LOGGER.info(f"User {user} created ")
    return user
