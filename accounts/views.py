from django.contrib.auth.views import LoginView
from accounts.forms import CustomLoginForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = CustomLoginForm


@login_required
def home(request):
    return render(request, "home.html")