from django.conf import settings
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from lists import views

urlpatterns = [
    path("new", views.new_list, name="new_list"),
    path("<int:list_id>/", views.view_list, name="view_list"),
]
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
