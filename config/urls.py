
from django.contrib import admin
from django.urls import path
from supermarket_online import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('produse/', views.lista_produse, name='lista_produse'),

    path('cos/', views.vizualizare_cos, name='vizualizare_cos'),
    path(
        'cos/adauga/<int:produs_id>/',
        views.adauga_in_cos,
        name='adauga_in_cos'
    ),
    path(
        'cos/actualizeaza/<int:produs_id>/',
        views.actualizare_cos,
        name='actualizare_cos'
    ),
    path(
        'cos/elimina/<int:produs_id>/',
        views.elimina_din_cos,
        name='elimina_din_cos'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
