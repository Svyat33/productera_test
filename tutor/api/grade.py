from rest_framework import viewsets, serializers, permissions

from tutor.models import Grade


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        fields = ['id', 'name']


class GroupView:
    queryset = Grade.objects.all().order_by('name')
    serializer_class = Serializer


class UserViewSet(GroupView, viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.AllowAny]


class AdminViewSet(GroupView, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
