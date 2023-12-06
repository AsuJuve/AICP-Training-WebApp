from django.urls import path
from .views import signup, home, LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

app_name = 'training'

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout',login_required(LogoutView.as_view()),name='logout'),
    path('', home, name='home')
]
