# -*- coding: utf-8 -*-
__author__ = 'Sergio Dzul'

"""
profiles forms
"""
import logging
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from profiles.models import CustomUser
from profiles.utils import create_hash

USER_MODEL = get_user_model()
logger = logging.getLogger(__name__)

REGEX_NAME = re.compile(r'^[a-zA-Záéíóúñ]+\S$', re.UNICODE)
MSG_NAME = _("No aceptan caracteres extraños, números, espacios.")
name_validator = RegexValidator(regex=REGEX_NAME, message=MSG_NAME)


class CustomUserForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label=_("Email address"),
        max_length=254)

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'gender',
                  'password1', 'password2', 'birthday',
                  'terms_and_conditions')

    def clean_password2(self):
        """
        Validate the two password are the same
        :return:
        """
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                _("The two password fields didn't match."),
                code='password_mismatch',
            )
        self.instance.username = self.cleaned_data.get('username')
        password_validation.validate_password(self.cleaned_data.get('password2'), self.instance)
        return password2

    def save(self, commit=True):
        user = super(CustomUserForm, self).save(commit=False)
        _password = self.cleaned_data["password1"]
        user.username = create_hash()
        user.set_password(_password)
        user.save()
        return user


class CustomSignupForm(UserCreationForm):
    def clean_username(self):
        """
        extra validation
        :return:
        """
        username = self.cleaned_data.get("username", "")

        regex = r'^([a-zA-Z.]*)$'
        if not re.match(regex, username):
            raise forms.ValidationError(
                message=_('You cannot use numbers'),
                code='invalid')

        if len(username) < 3:
            raise forms.ValidationError(
                message=_(u"Your username must be at least 3 letters"),
                code='invalid')

        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError(
                message=_('The username exist. Try with another'),
                code='invalid')

        return username


class EditProfileForm(forms.Form):
    user = {'username': None}
    error_messages = {
        'password_mismatch': _("The two passwords must match"),
    }

    first_name = forms.CharField(
        label=_("Name"),
        strip=False,
        required=False
    )

    last_name = forms.CharField(
        label=_("Last name"),
        strip=False,
        required=False
    )

    password = forms.CharField(
        label=_(u"Current password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput,
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        required=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        required=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    def __init__(self, username=None, **kwargs):
        super(EditProfileForm, self).__init__(**kwargs)
        self.user.update({'username': username})

    class Meta:
        fields = ("first_name", "last_name",
                  'password', 'password1',
                  'password2')

    def clean_password(self):
        password = self.cleaned_data.get("password")
        username = self.user.get("username")
        if password:
            user = USER_MODEL.objects.get(username=username)
            if not user.check_password(password):
                raise forms.ValidationError(_("Wrong password"))
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if not password1 and not password2:
            return
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        username = self.user.get("username")
        user = USER_MODEL.objects.get(username=username)
        password_validation.validate_password(self.cleaned_data.get('password2'), user)
        return password2

    def save(self):
        username = self.user.get("username")
        user = USER_MODEL.objects.get(username=username)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.set_password(self.cleaned_data.get("password"))
        user.save()


class RecoverPasswordForm(forms.Form):
    email = forms.EmailField(label="Email", )


class ChangePasswordForm(forms.Form):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=_("Repeat password"),
        widget=forms.PasswordInput,
        strip=False,
    )
