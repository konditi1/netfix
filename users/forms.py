from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, authenticate
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import User, Company, Customer


class DateInput(forms.DateInput):
    input_type = 'date'


def validate_email(value):
    # In case the email already exists in an email input in a registration form, this function is fired
    if User.objects.filter(email=value).exists():
        raise ValidationError(
            value + " is already taken.")


class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(
        validators=[validate_email],
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )
    date_of_birth = forms.DateField(
        widget=DateInput(attrs={'placeholder': 'Enter Date of Birth'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',  'email', 'password1', 'password2', 'date_of_birth')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and classes for the fields
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter Username', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})


    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_customer = True
        user.save()
        Customer.objects.create(user=user, date_of_birth=self.cleaned_data['date_of_birth'])
        return user


class CompanySignUpForm(UserCreationForm):
    email = forms.EmailField(validators=[validate_email])
    field = forms.ChoiceField(choices=Company._meta.get_field('field').choices,required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'field']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add placeholders and classes for the fields
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter Username', 'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter Email', 'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Enter Password', 'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password', 'class': 'form-control'})

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_company = True
        user.save()
        Company.objects.create(user=user, field=self.cleaned_data['field'])
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'})
    )