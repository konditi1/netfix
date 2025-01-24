from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from users.models import Company, Customer, User
from django.db.models import F

from .models import Service, ServiceRequest
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

    if company.field == "All in One":
        field_choices = Company.FIELD_CHOICES
    else:
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
            return redirect(reverse('services_field', kwargs={'field': company.field.replace(' ', '-').lower()}))
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


@login_required
def request_service(request, id):
    # Get the service object for the provided id
    service = get_object_or_404(Service, id=id)

    if request.method == 'POST':
        form = RequestServiceForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            address = form.cleaned_data['address']
            hours_required = form.cleaned_data['hours_required']

            # Increment the request count atomically to handle concurrent requests
            service.request_count = F('request_count') + 1
            service.save()
            service.refresh_from_db()  # Refresh to get the updated request_count value


            # Save the service request details
            ServiceRequest.objects.create(
                customer=request.user.customer,  
                service=service,
                address=address,
                hours_required=hours_required
            )


            # Provide feedback to the user
            messages.success(request, f"Service request for '{service.name}' created successfully!")
            return redirect("services_previous_request")
            # return redirect('service/previous_request', customer=request.user.customer)
        else:
            # If form is not valid, display errors
            messages.error(request, "There was an error in your request. Please check the form.")
    else:
        form = RequestServiceForm()

    return render(request, 'services/request_service.html', {'form': form, 'service': service})


@login_required
def previous_request(request):
    # Get the customer's previous service requests
    customer = request.user.customer
    previous_requests = ServiceRequest.objects.filter(customer=customer).select_related('service')

     # Add a total_cost attribute to each service request
    for service_request in previous_requests:
        service_request.total_cost = service_request.service.price_hour * service_request.hours_required


    # Render the `previous_request.html` template
    return render(
        request,
        "services/previous_request.html",
        {
            "customer": customer,
            "previous_requests": previous_requests,
        },
    )