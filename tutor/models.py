from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Grade(models.Model):
    name = models.CharField(_("Grade name"), max_length=255, unique=True)

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return self.__repr__()


class Speciality(models.Model):
    name = models.CharField(_("Speciality"), default="", unique=True, max_length=255)

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return self.__repr__()


class Language(models.Model):
    name = models.CharField(_("Language"), default="", unique=True, max_length=255)

    def __repr__(self):
        return f"{self.name}"

    def __str__(self):
        return self.__repr__()


class User(AbstractUser):
    phonenumber = models.CharField(_("Phone number"), max_length=150, default="")
    tutor = models.BooleanField(_("Tutor"), default=False)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL,
                              null=True)  # поведение при удалении типа образования стоит уточнить
    specialities = models.ManyToManyField(Speciality, )
    languages = models.ManyToManyField(Language, )
    max_cost = models.IntegerField(default=0)
    modify_time = models.DateTimeField(auto_now=True)

    class PossibleState(models.TextChoices):
        PENDING_APPROVAL = 'PAP', _('Pending Approval')
        PENDING_ASSUMPTION = 'PAS', _('Pending Assumption')
        APPROVED = 'APP', _('Approved')
        REJECTED = 'REJ', _('Rejected')
        NEW = 'NEW', _('Just registered')

    profile_status = models.CharField(max_length=3, default=PossibleState.NEW,
                                      choices=PossibleState.choices)

    tmp_changes = models.JSONField(default=dict)

    def __repr__(self):
        return f"{self.pk}| {self.username}"

    def __str__(self):
        return f"{self.pk}| {self.username} (T:{self.tutor})"

class ProfileChanges(models.Model):
    change_time = models.DateTimeField(auto_created=True, auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prev_state = models.CharField(max_length=3, choices=User.PossibleState.choices)
    next_state = models.CharField(max_length=3, choices=User.PossibleState.choices)
    changes = models.JSONField(default=dict)
