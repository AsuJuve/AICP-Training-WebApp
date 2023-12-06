from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import SignupForm, LoginForm
from .models import Competitor, Category
from django.contrib.auth.decorators import login_required
import requests

@login_required
def home(request):
    categories = Category.objects.all()
    return render(request, "home.html", {'categories': categories})

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if the user exists in Codeforces
            api_url = f'https://codeforces.com/api/user.info?handles={username}'
            response = requests.get(api_url)
            data = response.json()

            if response.status_code != 200:
                if data.get('status') != 'OK':
                    return render(request, 'accounts/signup.html', {
                        'form': form,
                        'error_message': 'Usuario de Codeforces incorrecto'
                    })
                
                return render(request, 'accounts/signup.html', {
                    'form': form,
                    'error_message': 'Conexión fallida con la API de Codeforces. Intente de nuevo más tarde.'
                })

            # Create a new Competitor user (adjust if needed based on your model)
            user = Competitor.objects.create_user(email=email, username=username, password=password)

            # Log in the user
            login(request, user)

            return redirect('training:home')

    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})

class LoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
