
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Produse


class PaginiPubliceSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "lista_produse",
            "despre_noi",
        ]

    def location(self, item):
        return reverse(item)


class ProduseSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Produse.objects.all()

    def location(self, item):
        return reverse(
            "detalii_produs",
            kwargs={"produs_id": item.pk}
        )
