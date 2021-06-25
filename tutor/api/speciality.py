from rest_framework import viewsets, serializers, permissions

from tutor.models import Speciality


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Speciality
        fields = ['id', 'name']

class GroupView:
    queryset = Speciality.objects.all().order_by('name')
    serializer_class = Serializer

class UserViewSet(GroupView, viewsets.ReadOnlyModelViewSet):
    permission_classes = []


class AdminViewSet(GroupView, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
