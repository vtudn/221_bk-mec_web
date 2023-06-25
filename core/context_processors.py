from core.models import Specialty


def specialties(request):
    specialties = Specialty.objects.all()
    return {'specialties': specialties}
