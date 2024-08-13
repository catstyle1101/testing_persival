import logging

from django.contrib import messages, auth
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse

from accounts.models import Token


logger = logging.getLogger(__name__)


def send_login_email(request):
    email = request.POST.get("email")
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse("login") + "?token=" + str(token.uid)
    )
    message_body = f"Use this link to log in:\n\n{url}"
    send_mail(
        "Your login link for Superlists",
        message_body,
        "noreply@superlists",
        [email]
    )
    messages.success(
        request,
        "Check your email for your login link for Superlists",
    )

    return redirect("/")


def login(request):
    logger.info("login view")
    uid = request.GET.get("token")
    user = auth.authenticate(request, uid=uid)
    if user is not None:
        auth.login(request, user)
    return redirect("/")


def logout(request):
    auth.logout(request)
    return redirect("/")
