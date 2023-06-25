from django.contrib import admin

from .models import Doctor, Specialty, Booking


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


class BookingAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'doctor',
                    'booked_date',
                    'payment_date',
                    'examination_date',
                    'address',
                    'description',
                    'total',
                    ]
    list_display_links = [
        'user',
        'doctor',
    ]
    list_filter = [
            'booked_date',
            'examination_date',
            ]
    # search_fields = [
    #     'user__username',
    #     'ref_code'
    # ]
    # actions = [make_refund_accepted]


admin.site.register(Specialty)
admin.site.register(Doctor)
admin.site.register(Booking, BookingAdmin)
