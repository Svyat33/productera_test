from django.urls import include, path
from rest_framework import routers
from . import grade, language, speciality, user

router = routers.DefaultRouter()
router.register(r'grade', grade.UserViewSet)
router.register(r'speciality', speciality.UserViewSet)
router.register(r'language', language.UserViewSet)
router.register(r'tutor', user.TutorSearchViewSet)

router.register(r'account/registration', user.RegisterViewSet)
router.register(r'account/profile', user.ProfileViewSet)

router.register(r'admin/grade', grade.AdminViewSet)
router.register(r'admin/speciality', speciality.AdminViewSet)
router.register(r'admin/language', language.AdminViewSet)
router.register(r'admin/user', user.AdminViewSet)