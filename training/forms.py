from django import forms
from .models import Competitor
from django.forms.widgets import PasswordInput, EmailInput
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.contrib.auth import authenticate
import requests

class SignupForm(forms.ModelForm):
    repassword = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar Contraseña',
        }),
        max_length = 32,
    )

    class Meta:
        model = Competitor
        fields = ['username', 'email', 'password', 'repassword']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Usuario de Codeforces'
                }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electrónico'
                }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contraseña'
                }),
        }

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def clean_password(self, *args, **kwargs):
        if self.data['password'] != self.data['repassword']:
            raise forms.ValidationError('Las contraseñas no coinciden')

        return self.data['password']

    def clean_username(self):
        username = self.cleaned_data['username']
        api_url = f'https://codeforces.com/api/user.info?handles={username}'

        response = requests.get(api_url)
        data = response.json()

        if response.status_code != 200:
            if data.get('status') != 'OK':
                raise forms.ValidationError('Usuario de Codeforces incorrecto')
            
            raise forms.ValidationError('Conexión fallida con la API de Codeforces. Intente de nuevo más tarde.')

        return username

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Correo electrónico'
    }))
    password = forms.CharField(widget=PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError('Credenciales incorrectas')
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
