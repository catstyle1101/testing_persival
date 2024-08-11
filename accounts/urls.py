from django.conf import settings
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from accounts import views

urlpatterns = [
    path("send_login_email/", views.send_login_email, name="send_login_email"),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
