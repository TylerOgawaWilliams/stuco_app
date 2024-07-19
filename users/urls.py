from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.sign_up, name="register"),
    path("confirm_email/", views.confirm_email, name="confirm_email"),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("reset_password/", views.reset_password, name="reset_password"),
]
