from http.client import HTTPResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.utils.translation import gettext_lazy as _
from users.models import CustomUser as User
from .forms import *
from .models import *
import datetime
from django.contrib import messages



class UserCreateView(View):
    def get(self, request, *args, **kwargs):
        context = {
            "form": BaseSignupForm(),
        }
        return render(request, "users/register.html", context=context)

    def post(self, request, *args, **kwargs):
        user_form = BaseSignupForm(request.POST)
        context = {
            "form": user_form,
        }
        if user_form.is_valid():
            user_form.save()
            user = authenticate(
                request,
                username=request.POST["email"],
                password=request.POST["password1"],
            )
            login(request, user)
            return redirect("pages:home")
        messages.error(request, "Please remove the form errors.")
        return render(request, "users/register.html", context=context)


class AccountSettingView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = {"form": BaseEditForm(instance=request.user)}
            return render(request, "users/account-settings.html", context=context)
        return redirect("login")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = BaseEditForm(request.POST, instance=request.user)
            context = {
                "form": form,
            }
            if form.is_valid():
                form.save()
                messages.success(request, "Account is updated successfully.")
            messages.error(request, "Please remove the form errors.")
            return render(request, "users/account-settings.html", context=context)
        return redirect("login")


class PasswordChangeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            context = {
                "form": UserPasswordChangeForm(self.request.user),
            }
            return render(request, "users/password-reset.html", context=context)
        return redirect("users:login")

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = UserPasswordChangeForm(request.user, request.POST)
            context = {
                "form": form,
            }
            if form.is_valid():
                form.save()
                messages.success(request, "Password is changed successfully.")
                update_session_auth_hash(self.request, form.user)
            messages.error(request, "Please remove the form errors.", "error")
            return render(request, "users/password-reset.html", context=context)
        return redirect("login")
