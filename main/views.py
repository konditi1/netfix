from django.shortcuts import render
from django.contrib.auth import logout as django_logout
from services.models import Service


def home(request):
    services = Service.objects.all()[:3]
    return render(request, "main/home.html", {"services": services})


def logout(request):
    django_logout(request)
    return render(request, "main/logout.html")
