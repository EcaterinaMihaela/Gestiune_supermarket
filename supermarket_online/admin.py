
from django.contrib import admin
from .models import CategoriiProduse, Raioane, Produse, ImagineProdus


admin.site.register(CategoriiProduse)
admin.site.register(Raioane)


class ImagineProdusInline(admin.StackedInline):
    model = ImagineProdus
    extra = 1
    max_num = 1


class ProduseAdmin(admin.ModelAdmin):
    inlines = [ImagineProdusInline]


admin.site.register(Produse, ProduseAdmin)