
from django.contrib import admin

from .models import (
    CategoriiProduse,
    Raioane,
    Produse,
    ImagineProdus,
    ProduseFurnizori,
    Furnizori
)


@admin.register(CategoriiProduse)
class CategoriiProduseAdmin(admin.ModelAdmin):
    search_fields = ("denumire",)


@admin.register(Raioane)
class RaioaneAdmin(admin.ModelAdmin):
    search_fields = ("denumire",)



@admin.register(Furnizori)
class FurnizoriAdmin(admin.ModelAdmin):
    list_display = ('id_furnizor', 'nume', 'adresa', 'tip')
    list_filter = ('tip',)
    search_fields = ('nume', 'adresa')



class ImagineProdusInline(admin.StackedInline):
    model = ImagineProdus
    extra = 0
    max_num = 1


@admin.register(Produse)
class ProduseAdmin(admin.ModelAdmin):

    list_display = (
        "id_produs",
        "denumire",
        "pret",
        "stoc",
        "id_categorie",
        "id_raion",
    )

    search_fields = ("denumire", "descriere")

    list_filter = (
        "id_categorie",
        "id_raion",
    )

    ordering = ("denumire",)

    list_per_page = 20

    inlines = [ImagineProdusInline]

    fieldsets = (
        ("Informații generale", {
            "fields": (
                "denumire",
                "descriere",
                "specificatii",
            )
        }),

        ("Preț și disponibilitate", {
            "fields": (
                "pret",
                "stoc",
            )
        }),

        ("Încadrare", {
            "fields": (
                "id_categorie",
                "id_raion",
            )
        }),

        ("Livrare", {
            "fields": (
                "modalitate_livrare",
            )
        }),
    )

@admin.register(ProduseFurnizori)
class ProduseFurnizoriAdmin(admin.ModelAdmin):
    list_display = (
        'id_produs_furnizor',
        'id_produs',
        'id_furnizor',
        'pret',
    )
    list_filter = ('id_furnizor',)
    search_fields = ('id_produs__denumire', 'id_furnizor__nume')
