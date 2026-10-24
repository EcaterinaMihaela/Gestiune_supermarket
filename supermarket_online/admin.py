
from django.contrib import admin
from .models import CategoriiProduse, Raioane, Produse, ImagineProdus


admin.site.register(CategoriiProduse)
admin.site.register(Raioane)


class ImagineProdusInline(admin.StackedInline):
    model = ImagineProdus
    extra = 0
    max_num = 1


@admin.register(Produse)
class ProduseAdmin(admin.ModelAdmin):
    list_display = ("id_produs", "denumire", "id_categorie", "id_raion")
    search_fields = ("denumire",)
    list_filter = ("id_categorie", "id_raion")
    inlines = [ImagineProdusInline]
