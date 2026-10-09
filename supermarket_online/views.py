
from django.shortcuts import render
from .models import Produse


def lista_produse(request):
    produse = Produse.objects.select_related(
        'id_categorie',
        'id_raion'
    ).all()

    return render(
        request,
        'supermarket_online/produse.html',
        {'produse': produse}
    )