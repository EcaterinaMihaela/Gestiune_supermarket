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