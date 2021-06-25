from rest_framework import viewsets, serializers, permissions

from tutor.models import Language


class Serializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'name']

class GroupView:
    queryset = Language.objects.all().order_by('name')
    serializer_class = Serializer

class UserViewSet(GroupView, viewsets.ReadOnlyModelViewSet):
    permission_classes = []


class AdminViewSet(GroupView, viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
