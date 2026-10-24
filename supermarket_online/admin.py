
from django.contrib import admin

from .models import (
    CategoriiProduse,
    Raioane,
    Produse,
    ImagineProdus,
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
        "id_categorie",
        "id_raion",
    )
    search_fields = ("denumire",)
    list_filter = ("id_categorie", "id_raion")
    inlines = [ImagineProdusInline]

