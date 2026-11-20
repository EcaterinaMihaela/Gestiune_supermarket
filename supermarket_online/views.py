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
from django.http import HttpResponse

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

    # Căutăm cea mai ieftină ofertă de la furnizori
    oferta_minima = (
        ProduseFurnizori.objects
        .filter(
            id_produs_id=produs_id,
            pret__isnull=False,
            pret__gt=0
        )
        .select_related('id_furnizor')
        .order_by('pret')
        .first()
    )

    # Dacă produsul nu are niciun furnizor cu ofertă validă
    if oferta_minima is None:
        return {
            'pret_initial': None,
            'pret_final': None,
            'procent_reducere': None,
            'are_promotie': False,
            'oferta_minima': None,
        }

    # Prețul inițial este prețul celui mai ieftin furnizor
    pret_initial = Decimal(str(oferta_minima.pret))

    azi = timezone.localdate()

    # Căutăm promoțiile active pentru produs
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

    promotie = max(
        promotii_active,
        key=lambda relatie: relatie.id_promotie.procent_reducere,
        default=None
    )

    # Dacă nu există promoție activă
    if promotie is None:
        return {
            'pret_initial': pret_initial,
            'pret_final': pret_initial,
            'procent_reducere': None,
            'are_promotie': False,
            'oferta_minima': oferta_minima,
        }

    # Aplicăm reducerea la prețul minim al furnizorului
    procent = Decimal(
        str(promotie.id_promotie.procent_reducere)
    )

    pret_final = (
        pret_initial * (Decimal('100') - procent) / Decimal('100')
    ).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )

    return {
        'pret_initial': pret_initial,
        'pret_final': pret_final,
        'procent_reducere': procent,
        'are_promotie': True,
        'oferta_minima': oferta_minima,
    }
def obtine_oferte_furnizori(produs_id):
    oferte = (
        ProduseFurnizori.objects
        .filter(
            id_produs_id=produs_id,
            pret__isnull=False,
            pret__gt=0
        )
        .select_related('id_furnizor')
        .order_by('pret')
    )

    azi = timezone.localdate()

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

    promotie = max(
        promotii_active,
        key=lambda relatie: relatie.id_promotie.procent_reducere,
        default=None
    )

    rezultat = []

    for oferta in oferte:
        pret_initial = Decimal(str(oferta.pret))

        if promotie:
            procent = Decimal(
                str(promotie.id_promotie.procent_reducere)
            )

            pret_final = (
                pret_initial * (Decimal('100') - procent)
                / Decimal('100')
            ).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
        else:
            procent = None
            pret_final = pret_initial

        rezultat.append({
            'oferta': oferta,
            'furnizor': oferta.id_furnizor,
            'pret_initial': pret_initial,
            'pret_final': pret_final,
            'procent_reducere': procent,
            'are_promotie': promotie is not None,
        })

    return rezultat

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
        produs.oferta_minima = detalii['oferta_minima']

        if produs.oferta_minima:
            produs.furnizor_minim = produs.oferta_minima.id_furnizor
        else:
            produs.furnizor_minim = None

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

def detalii_produs(request, produs_id):
    produs = get_object_or_404(
        Produse.objects.select_related(
            'id_categorie',
            'id_raion'
        ),
        pk=produs_id
    )

    detalii = obtine_detalii_pret(produs_id)

    produs.pret_initial = detalii['pret_initial']
    produs.pret_final = detalii['pret_final']
    produs.procent_reducere = detalii['procent_reducere']
    produs.are_promotie = detalii['are_promotie']

    produs.oferte_furnizori = obtine_oferte_furnizori(produs_id)

    try:
        produs.imagine_url = produs.imagine_produs.imagine.url
    except Exception:
        produs.imagine_url = None

    produse_similare = []

    if produs.id_categorie:
        produse_similare = list(
            Produse.objects.filter(
                id_categorie=produs.id_categorie
            ).exclude(
                pk=produs.pk
            )[:4]
        )

        for produs_similar in produse_similare:
            detalii_similar = obtine_detalii_pret(
                produs_similar.pk
            )

            produs_similar.pret_initial = detalii_similar['pret_initial']
            produs_similar.pret_final = detalii_similar['pret_final']
            produs_similar.are_promotie = detalii_similar['are_promotie']

            try:
                produs_similar.imagine_url = (
                    produs_similar.imagine_produs.imagine.url
                )
            except Exception:
                produs_similar.imagine_url = None

    return render(
        request,
        'supermarket_online/detalii_produs.html',
        {
            'produs': produs,
            'produse_similare': produse_similare,
        }
    )


@require_POST
def adauga_in_cos(request, produs_id):
    produs = get_object_or_404(Produse, pk=produs_id)

    try:
        cantitate = int(request.POST.get('cantitate', 1))
        id_furnizor = int(request.POST.get('id_furnizor'))
    except (TypeError, ValueError):
        messages.error(request, 'Selectează un furnizor și o cantitate validă.')
        return redirect('detalii_produs', produs_id=produs_id)

    if cantitate < 1:
        messages.error(request, 'Cantitatea trebuie să fie cel puțin 1.')
        return redirect('detalii_produs', produs_id=produs_id)

    oferta = ProduseFurnizori.objects.filter(
        id_produs_id=produs_id,
        id_furnizor_id=id_furnizor,
        pret__isnull=False,
        pret__gt=0
    ).select_related('id_furnizor').first()

    if oferta is None:
        messages.error(request, 'Oferta furnizorului selectat nu este disponibilă.')
        return redirect('detalii_produs', produs_id=produs_id)

    cos = request.session.get('cos', {})

    # Cheia identifică atât produsul, cât și furnizorul.
    cheie = f'{produs.pk}:{id_furnizor}'

    # Calculăm cantitatea totală a produsului, indiferent de furnizor.
    cantitate_existenta_produs = 0

    for cheie_existenta, cantitate_existenta in cos.items():
        try:
            id_produs_existenta = int(cheie_existenta.split(':')[0])
            if id_produs_existenta == produs.pk:
                cantitate_existenta_produs += int(cantitate_existenta)
        except (TypeError, ValueError):
            continue

    cantitate_totala = cantitate_existenta_produs + cantitate

    if produs.stoc <= 0:
        messages.error(request, 'Produsul nu este disponibil în stoc.')
        return redirect('detalii_produs', produs_id=produs_id)

    if cantitate_totala > produs.stoc:
        messages.warning(
            request,
            f'Poți adăuga maximum {produs.stoc} bucăți din acest produs, '
            'indiferent de furnizor.'
        )
        return redirect('detalii_produs', produs_id=produs_id)

    # Dacă produsul și furnizorul există deja, creștem cantitatea.
    cos[cheie] = int(cos.get(cheie, 0)) + cantitate

    request.session['cos'] = cos
    request.session.modified = True

    messages.success(
        request,
        f'{produs.denumire} de la {oferta.id_furnizor.nume} '
        'a fost adăugat în coș!'
    )

    return redirect('vizualizare_cos')


def vizualizare_cos(request):
    cos = request.session.get('cos', {})
    articole = []
    total = Decimal('0.00')
    numar_articole = 0

    for cheie, cantitate in cos.items():
        try:
            produs_id, id_furnizor = map(int, cheie.split(':'))
            cantitate = int(cantitate)
        except (TypeError, ValueError):
            continue

        if cantitate <= 0:
            continue

        produs = Produse.objects.filter(pk=produs_id).select_related(
            'id_categorie', 'id_raion'
        ).first()

        if produs is None:
            continue

        # Luăm oferta exactă a furnizorului selectat.
        oferte = obtine_oferte_furnizori(produs_id)

        detalii = next(
            (
                oferta
                for oferta in oferte
                if oferta['furnizor'].pk == id_furnizor
            ),
            None
        )

        if detalii is None:
            pret = None
            pret_initial = None
            furnizor = None
            procent_reducere = None
            are_promotie = False
            subtotal = None
        else:
            pret = detalii['pret_final']
            pret_initial = detalii['pret_initial']
            furnizor = detalii['furnizor']
            procent_reducere = detalii['procent_reducere']
            are_promotie = detalii['are_promotie']
            subtotal = pret * cantitate

            total += subtotal

        articole.append({
            'cheie': cheie,
            'produs': produs,
            'cantitate': cantitate,
            'id_furnizor': id_furnizor,
            'pret': pret,
            'pret_initial': pret_initial,
            'procent_reducere': procent_reducere,
            'are_promotie': are_promotie,
            'subtotal': subtotal,
            'furnizor': furnizor,
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
def actualizare_cos(request, produs_id, furnizor_id):
    cos = request.session.get('cos', {})
    cheie = f'{produs_id}:{furnizor_id}'

    if cheie in cos:
        try:
            cantitate = int(request.POST.get('cantitate', 1))
        except (TypeError, ValueError):
            cantitate = 1

        produs = get_object_or_404(Produse, pk=produs_id)

        if cantitate <= 0:
            cos.pop(cheie)
        else:
            cantitate_alte_oferte = 0

            for alta_cheie, alta_cantitate in cos.items():
                if alta_cheie == cheie:
                    continue

                try:
                    id_produs = int(alta_cheie.split(':')[0])
                    if id_produs == produs_id:
                        cantitate_alte_oferte += int(alta_cantitate)
                except (TypeError, ValueError):
                    continue

            cantitate_maxima = min(99, produs.stoc - cantitate_alte_oferte)

            if cantitate_maxima <= 0:
                messages.error(
                    request,
                    'Nu mai există stoc disponibil pentru acest produs.'
                )
            else:
                cos[cheie] = min(cantitate, cantitate_maxima)

                if cantitate > cantitate_maxima:
                    messages.warning(
                        request,
                        f'Cantitatea a fost limitată la {cantitate_maxima} '
                        'bucăți din cauza stocului disponibil.'
                    )

        request.session['cos'] = cos
        request.session.modified = True

    return redirect('vizualizare_cos')


@require_POST
def elimina_din_cos(request, produs_id, furnizor_id):
    cos = request.session.get('cos', {})
    cheie = f'{produs_id}:{furnizor_id}'

    cos.pop(cheie, None)

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
    # Obținem profilul clientului.
    # Dacă utilizatorul este administrator și nu are profil,
    # îl creăm pentru a putea testa plasarea comenzilor.
    client, creat = Clienti.objects.get_or_create(
        user=request.user,
        defaults={'nume': request.user.username}
    )

    cos = request.session.get('cos', {})

    if not cos:
        messages.warning(request, 'Coșul este gol!')
        return redirect('vizualizare_cos')

    if request.method == 'POST':
        form = FinalizareComandaForm(request.POST)

        if form.is_valid():

            # Citim și verificăm toate liniile coșului.
            articole_cos = []

            for cheie_cos, cantitate in cos.items():
                try:
                    produs_id, furnizor_id = map(
                        int, cheie_cos.split(':', 1)
                    )
                    cantitate = int(cantitate)

                except (TypeError, ValueError):
                    messages.error(
                        request,
                        'Coșul conține date invalide.'
                    )
                    return redirect('vizualizare_cos')

                if cantitate < 1 or cantitate > 99:
                    messages.error(request, 'Cantitate invalidă.')
                    return redirect('vizualizare_cos')

                articole_cos.append({
                    'produs_id': produs_id,
                    'furnizor_id': furnizor_id,
                    'cantitate': cantitate,
                })

            try:
                with transaction.atomic():

                    # Blocăm produsele pentru a evita modificări
                    # concurente ale stocului.
                    iduri_produse = {
                        articol['produs_id']
                        for articol in articole_cos
                    }

                    produse = Produse.objects.select_for_update().filter(
                        pk__in=iduri_produse
                    )

                    produse_dict = {
                        produs.pk: produs
                        for produs in produse
                    }

                    # Calculăm cantitatea totală pentru fiecare produs,
                    # chiar dacă apare de la mai mulți furnizori.
                    cantitati_totale = {}

                    for articol in articole_cos:
                        produs_id = articol['produs_id']

                        cantitati_totale[produs_id] = (
                            cantitati_totale.get(produs_id, 0)
                            + articol['cantitate']
                        )

                    # Verificăm existența produselor și stocul total.
                    for produs_id, cantitate_totala in cantitati_totale.items():
                        produs = produse_dict.get(produs_id)

                        if produs is None:
                            raise ValueError(
                                'Un produs din coș nu mai este disponibil.'
                            )

                        if produs.stoc < cantitate_totala:
                            raise ValueError(
                                f'Stoc insuficient pentru {produs.denumire}. '
                                f'Disponibil: {produs.stoc} bucăți.'
                            )

                    total = Decimal('0.00')
                    detalii_comanda = []

                    # Verificăm oferta exactă a fiecărui furnizor ales.
                    for articol in articole_cos:
                        produs = produse_dict[articol['produs_id']]
                        furnizor_id = articol['furnizor_id']
                        cantitate = articol['cantitate']

                        oferte = obtine_oferte_furnizori(produs.pk)

                        oferta_selectata = next(
                            (
                                oferta
                                for oferta in oferte
                                if oferta['furnizor'].pk == furnizor_id
                            ),
                            None
                        )

                        if oferta_selectata is None:
                            raise ValueError(
                                f'Oferta furnizorului selectat pentru '
                                f'{produs.denumire} nu mai este disponibilă.'
                            )

                        pret = Decimal(
                            str(oferta_selectata['pret_final'])
                        )

                        subtotal = pret * cantitate
                        total += subtotal

                        detalii_comanda.append({
                            'produs': produs,
                            'furnizor': oferta_selectata['furnizor'],
                            'cantitate': cantitate,
                            'pret': pret,
                        })

                    # Salvăm datele de livrare.
                    client.telefon = form.cleaned_data['telefon']
                    client.adresa = form.cleaned_data['adresa']
                    client.save(update_fields=['telefon', 'adresa'])

                    # Creăm comanda.
                    comanda = Comenzi.objects.create(
                        id_client=client,
                        data_comanda=timezone.now(),
                        total=total
                    )

                    # Salvăm fiecare poziție, inclusiv furnizorul ales.
                    for articol in detalii_comanda:
                        ProduseComenzi.objects.create(
                            id_comanda=comanda,
                            id_produs=articol['produs'],
                            id_furnizor=articol['furnizor'],
                            cantitate=articol['cantitate'],
                            pret_unitar=articol['pret']
                        )

                    # Scădem stocul o singură dată pentru fiecare produs.
                    for produs_id, cantitate_totala in cantitati_totale.items():
                        produs = produse_dict[produs_id]
                        produs.stoc -= cantitate_totala
                        produs.save(update_fields=['stoc'])

                    # Înregistrăm plata la livrare.
                    Plati.objects.create(
                        id_comanda=comanda,
                        metoda='Numerar la livrare',
                        suma=total,
                        data_plata=None
                    )

                # Golim coșul numai după salvarea cu succes.
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
                print(
                    "EROARE LA FINALIZAREA COMENZII:",
                    repr(e)
                )
                messages.error(
                    request,
                    f'Eroare la plasarea comenzii: {e}'
                )
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

def robots_txt(request):
    continut = f"""User-agent: *
Allow: /

Disallow: /admin/

Sitemap: {request.build_absolute_uri('/sitemap.xml')}
"""
    return HttpResponse(continut, content_type="text/plain")
