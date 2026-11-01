# This is an auto-generated Django model module.

# You'll have to do the following manually to clean this up:

#   * Rearrange models' order

#   * Make sure each model has one field with primary_key=True

#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior

#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table

# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.models import User




class Angajati(models.Model):

    cnp = models.CharField(primary_key=True, max_length=13)

    nume = models.CharField(max_length=100)

    adresa = models.CharField(max_length=200, blank=True, null=True)

    data_nasterii = models.DateField(blank=True, null=True)

    salariu = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    id_raion = models.ForeignKey('Raioane', models.DO_NOTHING, db_column='id_raion', blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'angajati'

    



class Casier(models.Model):

    cnp = models.OneToOneField(Angajati, models.DO_NOTHING, db_column='cnp', primary_key=True)



    class Meta:

        managed = False

        db_table = 'casier'





class CategoriiProduse(models.Model):

    id_categorie = models.IntegerField(primary_key=True)

    denumire = models.CharField(max_length=100)



    class Meta:

        managed = False

        db_table = 'categorii_produse'

    def __str__(self):
        return self.denumire



class Clienti(models.Model):
    id_client = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20, blank=True, null=True)
    adresa = models.CharField(max_length=200, blank=True, null=True)

    user = models.OneToOneField(
        User,
        on_delete=models.DO_NOTHING,
        db_column='user_id',
        blank=True,
        null=True,
        related_name='client_profile'
    )

    class Meta:
        managed = False
        db_table = 'clienti'

    def __str__(self):
        return self.nume




class Comenzi(models.Model):

    id_comanda = models.AutoField(primary_key=True)

    id_client = models.ForeignKey(Clienti, models.DO_NOTHING, db_column='id_client', blank=True, null=True)

    data_comanda = models.DateTimeField(blank=True, null=True)

    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'comenzi'






class Furnizori(models.Model):
    TIPURI_FURNIZOR = [
        ('ALIMENTARE', 'Produse alimentare'),
        ('LACTATE', 'Lactate și brânzeturi'),
        ('FRUCTE_LEGUME', 'Fructe și legume'),
        ('PANIFICATIE', 'Panificație'),
        ('BAUTURI', 'Băuturi'),
        ('CURATENIE', 'Produse de curățenie'),
        ('DIVERSE', 'Produse diverse'),
    ]

    id_furnizor = models.IntegerField(primary_key=True)
    nume = models.CharField(max_length=150)
    adresa = models.CharField(max_length=200, blank=True, null=True)
    tip = models.CharField(
        max_length=30,
        choices=TIPURI_FURNIZOR,
        default='DIVERSE'
    )

    class Meta:
        managed = False
        db_table = 'furnizori'

    def __str__(self):
        return self.nume




class LucratorRaion(models.Model):

    cnp = models.OneToOneField(Angajati, models.DO_NOTHING, db_column='cnp', primary_key=True)



    class Meta:

        managed = False

        db_table = 'lucrator_raion'





class Manager(models.Model):

    cnp = models.OneToOneField(Angajati, models.DO_NOTHING, db_column='cnp', primary_key=True)



    class Meta:

        managed = False

        db_table = 'manager'





class Plati(models.Model):
    id_plata = models.AutoField(primary_key=True)

    id_comanda = models.ForeignKey(
        'Comenzi',
        models.DO_NOTHING,
        db_column='id_comanda',
        blank=True,
        null=True
    )

    metoda = models.CharField(max_length=30, blank=True, null=True)

    suma = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    data_plata = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plati'






class Produse(models.Model):
    id_produs = models.IntegerField(primary_key=True)

    denumire = models.CharField(max_length=150)

    id_raion = models.ForeignKey(
        'Raioane',
        models.DO_NOTHING,
        db_column='id_raion',
        blank=True,
        null=True
    )

    id_categorie = models.ForeignKey(
        CategoriiProduse,
        models.DO_NOTHING,
        db_column='id_categorie',
        blank=True,
        null=True
    )

    descriere = models.TextField(blank=True, null=True)

    specificatii = models.TextField(blank=True, null=True)

    pret = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    stoc = models.PositiveIntegerField(default=0)

    modalitate_livrare = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'produse'

    def __str__(self):
        return self.denumire



class ProduseComenzi(models.Model):

    pk = models.CompositePrimaryKey('id_comanda', 'id_produs')

    id_comanda = models.ForeignKey(Comenzi, models.DO_NOTHING, db_column='id_comanda')

    id_produs = models.ForeignKey(Produse, models.DO_NOTHING, db_column='id_produs')

    cantitate = models.IntegerField(blank=True, null=True)

    pret_unitar = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'produse_comenzi'






class ProduseFurnizori(models.Model):
    id_produs_furnizor = models.AutoField(primary_key=True)

    id_produs = models.ForeignKey(
        'Produse',
        models.DO_NOTHING,
        db_column='id_produs'
    )

    id_furnizor = models.ForeignKey(
        'Furnizori',
        models.DO_NOTHING,
        db_column='id_furnizor'
    )

    pret = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    class Meta:
        managed = False
        db_table = 'produse_furnizori'
        unique_together = (('id_produs', 'id_furnizor'),)

    def __str__(self):
        return f"{self.id_produs} - {self.id_furnizor}: {self.pret} lei"




class ProdusePromotii(models.Model):

    pk = models.CompositePrimaryKey('id_produs', 'id_promotie')

    id_produs = models.ForeignKey(Produse, models.DO_NOTHING, db_column='id_produs')

    id_promotie = models.ForeignKey('Promotii', models.DO_NOTHING, db_column='id_promotie')



    class Meta:

        managed = False

        db_table = 'produse_promotii'





class Promotii(models.Model):

    id_promotie = models.IntegerField(primary_key=True)

    denumire = models.CharField(max_length=100)

    data_start = models.DateField(blank=True, null=True)

    data_sfarsit = models.DateField(blank=True, null=True)

    procent_reducere = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'promotii'





class Raioane(models.Model):

    id_raion = models.IntegerField(primary_key=True)

    nume_raion = models.CharField(max_length=100)



    class Meta:

        managed = False

        db_table = 'raioane'


    def __str__(self):
        return self.nume_raion


class SefiRaion(models.Model):

    id_raion = models.OneToOneField(Raioane, models.DO_NOTHING, db_column='id_raion', primary_key=True)

    cnp_sef = models.ForeignKey(Angajati, models.DO_NOTHING, db_column='cnp_sef')



    class Meta:

        managed = False

        db_table = 'sefi_raion'


class ImagineProdus(models.Model):
    produs = models.OneToOneField(
        Produse,
        on_delete=models.CASCADE,
        db_column='id_produs',
        primary_key=True,
        related_name='imagine_produs'
    )

    imagine = models.ImageField(upload_to='produse/')

    class Meta:
        managed = True
        db_table = 'imagini_produse'
        verbose_name = 'Imagine produs'
        verbose_name_plural = 'Imagini produse'

    def __str__(self):
        return f'Imagine pentru {self.produs.denumire}'