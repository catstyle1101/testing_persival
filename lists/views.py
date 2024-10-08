from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect

from lists.forms import ItemForm, ExistingListItemForm, NewListForm
from lists.models import List

User = get_user_model()


def home_page(request):
    """Домашняя страница."""
    print("hello")
    return render(request, "home.html", {"form": ItemForm()})


def view_list(request, list_id):
    """Представление списка."""
    list_ = List.objects.get(pk=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == "POST":
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)
    return render(
        request,
        "list.html",
        {
            "form": form,
            "list": list_,
        },
    )


def new_list(request):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, "home.html", {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, "my_lists.html", {"owner": owner})


def share(request, list_id):
    list_ = List.objects.get(pk=list_id)
    shared_user_email = request.POST.get("sharee")
    user = User.objects.get_or_create(email=shared_user_email)[0]
    list_.shared_with.add(user)
    return redirect(list_)
