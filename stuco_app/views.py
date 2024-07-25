# Create your views here.
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages


def about(request):
    messages.add_message(request, messages.SUCCESS, "This is a sample success message from the about page.")
    messages.add_message(request, messages.INFO, "This is a sample info message from the about page.")
    messages.add_message(request, messages.ERROR, "This is a sample error message from the about page.")
    return render(request, "about.html")


def home(request):
    if not request.user.is_authenticated:
        messages.add_message(request, messages.INFO, "Note: Login for access to all features . . .")

    return render(request, "home.html")


def django_login(request):
    # return redirect("/admin/login/?next=/")
    return redirect("/accounts/login/?next=/")
