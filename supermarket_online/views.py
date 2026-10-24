
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Produse, ProduseFurnizori



def lista_produse(request):
    produse = Produse.objects.select_related(
        'id_categorie',
        'id_raion'
    ).all()

    categorii = (
        Produse.objects
        .exclude(id_categorie__isnull=True)
        .values(
            'id_categorie',
            'id_categorie__denumire'
        )
        .distinct()
        .order_by('id_categorie__denumire')
    )

    return render(
        request,
        'supermarket_online/produse.html',
        {
            'produse': produse,
            'categorii': categorii,
        }
    )



def obtine_pret(produs_id):
    preturi = ProduseFurnizori.objects.filter(
        id_produs_id=produs_id,
        pret__isnull=False,
        pret__gte=0
    ).order_by('pret')

    pret = preturi.values_list('pret', flat=True).first()
    return pret


@require_POST
def adauga_in_cos(request, produs_id):
    produs = get_object_or_404(Produse, pk=produs_id)

    try:
        cantitate = int(request.POST.get('cantitate', 1))
    except (TypeError, ValueError):
        cantitate = 1

    cantitate = max(1, min(cantitate, 99))

    cos = request.session.get('cos', {})
    id_produs = str(produs.pk)

    try:
        cantitate_existenta = int(cos.get(id_produs, 0))
    except (TypeError, ValueError):
        cantitate_existenta = 0

    cos[id_produs] = min(cantitate_existenta + cantitate, 99)

    request.session['cos'] = cos
    request.session.modified = True

    return redirect('lista_produse')


def vizualizare_cos(request):
    cos = request.session.get('cos', {})
    articole = []
    total = Decimal('0.00')
    numar_articole = 0

    for id_produs, cantitate in cos.items():
        try:
            cantitate = int(cantitate)
            produs_id = int(id_produs)
        except (TypeError, ValueError):
            continue

        if cantitate <= 0:
            continue

        produs = Produse.objects.filter(pk=produs_id).first()

        if produs is None:
            continue

        pret = obtine_pret(produs_id)
        subtotal = None

        if pret is not None:
            pret = Decimal(str(pret))
            subtotal = pret * cantitate
            total += subtotal

        articole.append({
            'produs': produs,
            'cantitate': cantitate,
            'pret': pret,
            'subtotal': subtotal,
        })

        numar_articole += cantitate

    return render(
        request,
        'supermarket_online/cos.html',
        {
            'articole': articole,
            'cos_gol': not bool(articole),
            'total': total,
            'numar_articole': numar_articole,
            'preturi_complete': all(
                articol['pret'] is not None for articol in articole
            ),
        }
    )


@require_POST
def actualizare_cos(request, produs_id):
    cos = request.session.get('cos', {})
    id_produs = str(produs_id)

    if id_produs in cos:
        try:
            cantitate = int(request.POST.get('cantitate', 1))
        except (TypeError, ValueError):
            cantitate = 1

        if cantitate <= 0:
            cos.pop(id_produs)
        else:
            cos[id_produs] = min(cantitate, 99)

        request.session['cos'] = cos
        request.session.modified = True

    return redirect('vizualizare_cos')


@require_POST
def elimina_din_cos(request, produs_id):
    cos = request.session.get('cos', {})
    cos.pop(str(produs_id), None)

    request.session['cos'] = cos
    request.session.modified = True

    return redirect('vizualizare_cos')
