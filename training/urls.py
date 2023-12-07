from django.urls import path
from .views import signup, home, category_detail, request_recommendation, request_diagnosis, LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView

app_name = 'training'

urlpatterns = [
    path('', home, name='home'),
    path('category/<int:category_id>/', category_detail, name='category_detail'),
    path('request_recommendation/<int:category_id>/', request_recommendation, name='request_recommendation'),
    path('request_diagnosis/<int:category_id>/', request_diagnosis, name='request_diagnosis'),
    path('signup/', signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout',login_required(LogoutView.as_view()),name='logout')
]
