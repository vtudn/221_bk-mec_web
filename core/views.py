import random
import string

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from core.momo.collection_link import *

from .forms import CheckoutForm
from .models import Doctor, Specialty, Booking

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            context = {
                'form': form,
                'doctor': Doctor.objects.get(pk=kwargs['pk'])
            }
            return render(self.request, "booking-new.html", context)
        except ObjectDoesNotExist:
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            if form.is_valid():
                doctor = Doctor.objects.get(pk=kwargs['pk'])
                payment_option = form.cleaned_data.get('payment_option')
                examination_date = form.cleaned_data.get('examination_date')
                address = form.cleaned_data.get('address')
                description = form.cleaned_data.get('description')
                booking = Booking.objects.create(examination_date=examination_date,
                        user=self.request.user, total=doctor.price, doctor=doctor,
                        address=address, description=description)
                if payment_option == 'M':
                    momo_response = momo_payment(booking.total, booking.pk)
                    return redirect(momo_response['payUrl'])
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class HomeView(ListView):
    model = Doctor
    paginate_by = 8
    template_name = "home.html"
    def get_queryset(self):
        try:
            specialty = Specialty.objects.get(slug=self.request.GET.get('specialty'))
        except:
            specialty = None
        search = self.request.GET.get('search')
        if search: return Doctor.objects.filter(name__contains=search)
        return Doctor.objects.filter(specialties=specialty) if specialty else Doctor.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            specialty = Specialty.objects.get(slug=self.request.GET.get('specialty'))
        except:
            specialty = None
        context['filter_specialty'] = specialty
        context['recommended_doctors'] = Doctor.objects.all()[:3]
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            bookings = Booking.objects.filter(user=self.request.user).order_by('-booked_date')
            context = {
                'bookings': bookings
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class DoctorDetailView(DetailView):
    model = Doctor
    template_name = "doctor.html"

    def get_context_data(self, **kwargs):
        context = super(DoctorDetailView, self).get_context_data(**kwargs)
        context['items'] = Doctor.objects.exclude(pk=self.object.pk).order_by('?')[:3]
        return context


def checkout_success(request):
    booking = Booking.objects.get(pk=request.GET.get('pk'))
    booking.payment_date = timezone.now()
    booking.save()
    messages.success(request, "Your booking was set up successfully")
    return redirect("/")

def proceed_payment(request, pk):
    booking = Booking.objects.get(pk=pk)
    momo_response = momo_payment(booking.total, booking.pk)
    return redirect(momo_response['payUrl'])
