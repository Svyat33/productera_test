from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from tutor.api import router

urlpatterns = [
    path('', include(router.urls)),

    path("account/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("account/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("account/token/health/", TokenVerifyView.as_view(), name="check_token"),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
