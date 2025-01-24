from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.views.generic import CreateView, TemplateView

from .forms import CustomerSignUpForm, CompanySignUpForm, UserLoginForm
from .models import User, Company, Customer
from django.shortcuts import render


def register(request):
    return render(request, 'users/register.html')


class CustomerSignUpView(CreateView):
    model = User
    form_class = CustomerSignUpForm
    template_name = 'users/register_customer.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'customer'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/profile')


class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'users/register_company.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('/profile', name=user.username)


def LoginUserView(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/profile')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()

    return render(request, 'users/login.html', {'form': form})


def user_profile(request):
    if not request.user.is_authenticated:
        return redirect('login_user')
    
    context = {
        'user': request.user,
    }
    
    if request.user.is_customer:
        # # Fetch customer-specific data
        # requested_services = request.user.customer.requested_services.all()  # Example queryset
        # context['services'] = requested_services
        context['is_customer'] = True
    elif request.user.is_company:
        # Fetch company-specific data
        # created_services = request.user.company.services.all()  # Example queryset
        # context['services'] = created_services
        context['is_company'] = True

    return render(request, 'users/profile.html', context)

