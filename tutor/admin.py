from django.contrib import admin
from .models import User, Grade, Language, Speciality, ProfileChanges
# Register your models here.
admin.site.register(User)
admin.site.register(Language)
admin.site.register(Grade)
admin.site.register(ProfileChanges)
admin.site.register(Speciality)