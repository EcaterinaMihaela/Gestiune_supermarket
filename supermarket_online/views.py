from decimal import Decimal, ROUND_HALF_UP

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import EditareContForm
from django.db import transaction
from supermarket_online.models import Clienti

from .models import Produse, ProduseFurnizori, ProdusePromotii
from .forms import EditareContForm, FinalizareComandaForm

from .models import (
    Clienti,
    Produse,
    ProduseFurnizori,
    ProdusePromotii,
    Comenzi,
    ProduseComenzi,
    Plati,
)


def obtine_detalii_pret(produs_id):
    # Cel mai mic pret dintre furnizorii produsului
    pret_initial = (
        ProduseFurnizori.objects
        .filter(
            id_produs_id=produs_id,
            pret__isnull=False,
            pret__gte=0
        )
        .order_by('pret')
        .values_list('pret', flat=True)
        .first()
    )

    if pret_initial is None:
        return {
            'pret_initial': None,
            'pret_final': None,
            'procent_reducere': None,
            'are_promotie': False,
        }

    pret_initial = Decimal(str(pret_initial))
    azi = timezone.localdate()

    # Cautam promotiile active pentru produs
    promotii_active = (
        ProdusePromotii.objects
        .filter(
            id_produs_id=produs_id,
            id_promotie__data_start__lte=azi,
            id_promotie__data_sfarsit__gte=azi,
            id_promotie__procent_reducere__gt=0,
            id_promotie__procent_reducere__lte=100,
        )
        .select_related('id_promotie')
    )

    # Daca exista mai multe promotii active, o alegem pe cea mai mare
    promotie = max(
        promotii_active,
        key=lambda relatie: relatie.id_promotie.procent_reducere,
        default=None
    )

    if promotie is None:
        return {
            'pret_initial': pret_initial,
            'pret_final': pret_initial,
            'procent_reducere': None,
            'are_promotie': False,
        }

    procent = Decimal(str(
        promotie.id_promotie.procent_reducere
    ))

    pret_final = (
        pret_initial * (Decimal('100') - procent) / Decimal('100')
    ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    return {
        'pret_initial': pret_initial,
        'pret_final': pret_final,
        'procent_reducere': procent,
        'are_promotie': True,
    }


def lista_produse(request):
    produse = list(
        Produse.objects.select_related(
            'id_categorie',
            'id_raion'
        ).all()
    )

    for produs in produse:
        detalii = obtine_detalii_pret(produs.pk)

        produs.pret_initial = detalii['pret_initial']
        produs.pret_final = detalii['pret_final']
        produs.procent_reducere = detalii['procent_reducere']
        produs.are_promotie = detalii['are_promotie']

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


@require_POST
def adauga_in_cos(request, produs_id):
    produs = get_object_or_404(Produse, pk=produs_id)

    try:
        cantitate = int(request.POST.get('cantitate', 1))
    except (TypeError, ValueError):
        cantitate = 1

    cantitate = max(1, min(cantitate, 99))

    cos = request.session.get('cos', {})
    print("COS PRIMIT:", cos)
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

        detalii = obtine_detalii_pret(produs_id)

        pret = detalii['pret_final']
        pret_initial = detalii['pret_initial']
        subtotal = None

        if pret is not None:
            subtotal = pret * cantitate
            total += subtotal

        articole.append({
            'produs': produs,
            'cantitate': cantitate,
            'pret': pret,
            'pret_initial': pret_initial,
            'procent_reducere': detalii['procent_reducere'],
            'are_promotie': detalii['are_promotie'],
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
                articol['pret'] is not None
                for articol in articole
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


def inregistrare(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            print("FORMULAR VALID:", form.is_valid())
            print("ERORI FORMULAR:", form.errors)
            try:
                with transaction.atomic():
                    user = form.save()

                    Clienti.objects.create(
                        nume=user.username,
                        user=user
                    )

                login(request, user)
                messages.success(
                    request,
                    'Contul a fost creat cu succes!'
                )
                return redirect('lista_produse')

            except IntegrityError as e:
                print("EROARE LA CREAREA CONTULUI:", repr(e))
                messages.error(request, f"Eroare baza de date: {e}")

    else:
        form = UserCreationForm()

    return render(
        request,
        'supermarket_online/inregistrare.html',
        {'form': form}
    )

@login_required
def contul_meu(request):
    if request.method == "POST":
        form = EditareContForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, "Datele contului au fost actualizate!")
            return redirect("contul_meu")
    else:
        form = EditareContForm(instance=request.user)

    return render(
        request,
        "supermarket_online/contul_meu.html",
        {"form": form}
    )

def despre_noi(request):
    return render(
        request,
        "supermarket_online/despre_noi.html"
    )



@login_required
def finalizare_comanda(request):
    client = get_object_or_404(Clienti, user=request.user)

    cos = request.session.get('cos', {})

    if not cos:
        messages.warning(request, 'Coșul este gol!')
        return redirect('vizualizare_cos')

    if request.method == 'POST':
        form = FinalizareComandaForm(request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Verificam si blocam produsele pentru actualizarea stocului
                    articole_cos = []

                    for id_produs, cantitate in cos.items():
                        try:
                            produs_id = int(id_produs)
                            cantitate = int(cantitate)
                        except (TypeError, ValueError):
                            messages.error(request, 'Coșul conține date invalide.')
                            return redirect('vizualizare_cos')

                        if cantitate < 1 or cantitate > 99:
                            messages.error(request, 'Cantitate invalidă.')
                            return redirect('vizualizare_cos')

                        articole_cos.append((produs_id, cantitate))

                    produse = Produse.objects.select_for_update().filter(
                        pk__in=[item[0] for item in articole_cos]
                    )

                    produse_dict = {
                        produs.pk: produs for produs in produse
                    }

                    total = Decimal('0.00')
                    detalii_comanda = []

                    # Verificam produsele, stocul si preturile
                    for produs_id, cantitate in articole_cos:
                        produs = produse_dict.get(produs_id)

                        if produs is None:
                            raise ValueError(
                                'Un produs din coș nu mai este disponibil.'
                            )

                        if produs.stoc < cantitate:
                            raise ValueError(
                                f'Stoc insuficient pentru {produs.denumire}. '
                                f'Disponibil: {produs.stoc}.'
                            )

                        detalii_pret = obtine_detalii_pret(produs_id)
                        pret = detalii_pret['pret_final']

                        if pret is None:
                            raise ValueError(
                                f'Produsul {produs.denumire} nu are un preț disponibil.'
                            )

                        pret = Decimal(str(pret))
                        subtotal = pret * cantitate
                        total += subtotal

                        detalii_comanda.append({
                            'produs': produs,
                            'cantitate': cantitate,
                            'pret': pret,
                        })

                    # Salvam datele de livrare ale clientului
                    client.telefon = form.cleaned_data['telefon']
                    client.adresa = form.cleaned_data['adresa']
                    client.save(update_fields=['telefon', 'adresa'])

                    # Cream comanda
                    print("TOTAL COMANDA:", total)
                    print("PRODUSE COMANDA:", detalii_comanda)
                    comanda = Comenzi.objects.create(
                        id_client=client,
                        data_comanda=timezone.now(),
                        total=total
                    )

                    # Salvam produsele si actualizam stocul
                    for articol in detalii_comanda:
                        produs = articol['produs']
                        cantitate = articol['cantitate']

                        ProduseComenzi.objects.create(
                            id_comanda=comanda,
                            id_produs=produs,
                            cantitate=cantitate,
                            pret_unitar=articol['pret']
                        )

                        produs.stoc -= cantitate
                        produs.save(update_fields=['stoc'])

                    # Inregistram plata la livrare
                    Plati.objects.create(
                        id_comanda=comanda,
                        metoda='Numerar la livrare',
                        suma=total,
                        data_plata=None
                    )

                # Golim cosul numai dupa salvarea cu succes
                request.session['cos'] = {}
                request.session.modified = True

                messages.success(
                    request,
                    f'Comanda #{comanda.id_comanda} a fost plasată cu succes! '
                    f'Total: {total:.2f} lei.'
                )

                return redirect(
                    'confirmare_comanda',
                    id_comanda=comanda.id_comanda
                )

            except Exception as e:
                print("EROARE LA FINALIZAREA COMENZII:", repr(e))
                messages.error(request, f"Eroare la plasarea comenzii: {e}")
                return redirect('vizualizare_cos')

    else:
        form = FinalizareComandaForm(initial={
            'telefon': client.telefon or '',
            'adresa': client.adresa or '',
        })

    return render(
        request,
        'supermarket_online/finalizare_comanda.html',
        {
            'form': form,
            'client': client,
        }
    )


@login_required
def confirmare_comanda(request, id_comanda):
    client = get_object_or_404(Clienti, user=request.user)

    comanda = get_object_or_404(
        Comenzi,
        id_comanda=id_comanda,
        id_client=client
    )

    articole = ProduseComenzi.objects.filter(
        id_comanda=comanda
    ).select_related('id_produs')

    plata = Plati.objects.filter(
        id_comanda=comanda
    ).first()

    return render(
        request,
        'supermarket_online/confirmare_comanda.html',
        {
            'comanda': comanda,
            'articole': articole,
            'plata': plata,
        }
    )