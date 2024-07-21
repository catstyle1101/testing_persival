from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect

from lists.forms import ItemForm
from lists.models import Item, List


def home_page(request):
    """Домашняя страница."""
    return render(request, "home.html", {"form": ItemForm()})


def view_list(request, list_id):
    """Представление списка."""
    list_ = List.objects.get(pk=list_id)
    form = ItemForm()
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            Item.objects.create(
                text=form.cleaned_data["text"],
                list=list_,
            )
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
    """Новый список."""
    form = ItemForm(data=request.POST)
    if form.is_valid():
        list_ = List.objects.create()
        Item.objects.create(text=request.POST["text"], list=list_)
        return redirect(list_)
    return render(request, "home.html", {"form": form})
