
from django import forms
from django.contrib.auth.models import User


class EditareContForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        labels = {
            'first_name': 'Prenume',
            'last_name': 'Nume',
            'email': 'Adresă de email',
        }

        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introdu prenumele'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introdu numele'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Introdu adresa de email'
            }),
        }


class FinalizareComandaForm(forms.Form):
    telefon = forms.CharField(
        label='Număr de telefon',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Introdu numărul de telefon'
        })
    )

    adresa = forms.CharField(
        label='Adresa de livrare',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Stradă, număr, localitate'
        })
    )

    metoda_plata = forms.ChoiceField(
        label='Metoda de plată',
        choices=[
            ('RAMBURS', 'Numerar la livrare'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
