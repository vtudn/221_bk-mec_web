from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.utils.text import slugify



LABEL_CHOICES = (
    ('P', 'danger'),
    ('S', 'secondary'),
    ('D', 'primary')
)

TITLE_MAP = {
        'P': 'Professor',
        'S': 'PhD',
        'D': 'Dr.'
        }

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)


def construct_color_map():
    COLOR_CONSTRUCTOR = {
            'purple': ['dermatology'],
            'primary-color': ['ophthalmology'],
            'secondary-color': ['internal-medicine'],
            'danger-color': ['surgery'],
            }
    res = {}
    for color, affected_list in COLOR_CONSTRUCTOR.items():
        for i in affected_list:
            res[i] = color
    return res

BADGE_COLOR_MAP = construct_color_map()


class Specialty(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Specialty, self).save(*args, **kwargs)



    def __str__(self):
        return self.name


    @property
    def badge_color(self):
        return BADGE_COLOR_MAP[self.slug] if self.slug in BADGE_COLOR_MAP else 'primary-color'

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    specialties = models.ManyToManyField(Specialty)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Doctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'pk': self.pk,
            'slug': self.slug,
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_booking_url(self):
        return reverse("core:booking", kwargs={
            'pk': self.pk
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    @property
    def short_description(self):
        return self.description[:100]

    def title(self):
        return TITLE_MAP[self.label]


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    booked_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(default=None, null=True)
    examination_date = models.DateTimeField()
    address = models.CharField(max_length=500)
    total = models.FloatField(default=0)
    description = models.TextField(default='', null=True, blank=True)


    def get_proceed_payment_url(self):
        return reverse('core:booking-proceed-payment', kwargs={'pk': self.pk})


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
