from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from users.models import Company, Customer, User

from .models import Service
from .forms import CreateNewService, RequestServiceForm


def service_list(request):
    services = Service.objects.all().order_by("-date")
    return render(request, 'services/list.html', {'services': services})


def index(request, id):
    service = Service.objects.get(id=id)
    return render(request, 'services/single_service.html', {'service': service})

@login_required
def create(request):
    # Get the company linked to the logged-in user
    company = request.user.company
    field_choices = [(company.field, company.field)]

    if request.method == "POST":
        form = CreateNewService(request.POST, choices=field_choices)
        if form.is_valid():
            # Save the new service
            Service.objects.create(
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                field=form.cleaned_data['field'],
                price_hour=form.cleaned_data['price_hour'],
                company=company,
            )
            messages.success(request, "Service created successfully!")
            print('message',messages)
            return redirect('/')  
        else:
            print('error messages',form.errors)
    else:
        form = CreateNewService(choices=field_choices)

    return render(request, 'services/create.html', {'form': form})


def service_field(request, field):
    # search for the service present in the url
    field = field.replace('-', ' ').title()
    services = Service.objects.filter(
        field=field)
    return render(request, 'services/field.html', {'services': services, 'field': field})


def request_service(request, id):
    return render(request, 'services/request_service.html', {})
