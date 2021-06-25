import datetime

from rest_framework import serializers, permissions, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django.db import models
from tutor.models import User, Speciality, Language, ProfileChanges
from .speciality import Serializer as SpecialitySerializer
from .language import Serializer as LanguageSerializer


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'tutor']
        extra_kwargs = {
            'password': {'write_only': True, 'style': {'input_type': 'password'}}
        }

    def validate_password2(self, value):
        if not self.initial_data['password'] == value:
            raise serializers.ValidationError({'password': 'password and password2 should be equal'})
        return value

    def validate_password(self, value):
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        return value

    def save(self, **kwargs):
        account = User(username=self.validated_data['username'],
                       tutor=self.validated_data['tutor'])
        account.set_password(self.validated_data['password'])
        account.save()
        return account


class ProfileSerializer(serializers.ModelSerializer):
    specialities = SpecialitySerializer(many=True, read_only=True)
    specialitieslist = serializers.JSONField(write_only=True)

    languages = LanguageSerializer(many=True, read_only=True)
    languageslist = serializers.JSONField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phonenumber', 'specialities', 'languages', 'languageslist', 'grade',
                  'max_cost', 'specialitieslist',
                  'tmp_changes', 'profile_status']
        extra_kwargs = {
            'profile_status': {'read_only': True, },
            'username': {'read_only': True, },
            'tmp_changes': {'read_only': True},
            'specialities': {'read_only': True},
            'specialitieslist': {'write_only': True},
            'languages': {'read_only': True},
            'languageslist': {'write_only': True},
        }

    def validate_specialitieslist(self, val):
        if not type(val) is list:
            serializers.ValidationError({'specialitieslist': 'Should be JSON list of integers'})
        return val

    def validate_languageslist(self, val):
        if not type(val) is list:
            serializers.ValidationError({'languageslist': 'Should be JSON list of integers'})
        return val

    def save(self, **kwargs):
        self.instance: User
        changes = {}
        for k in self.validated_data:
            if hasattr(self.instance, k) and getattr(self.instance, k) != self.validated_data[k]:
                if isinstance(self.validated_data[k], models.Model):
                    changes[k] = self.validated_data[k].pk
                else:
                    changes[k] = self.validated_data[k]

        current_spec = {s[0] for s in self.instance.specialities.all().values_list('id')}
        new_spec = {s.id for s in Speciality.objects.filter(id__in=self.validated_data['specialitieslist'])}
        if current_spec != new_spec:
            changes['specialities'] = list(new_spec)

        current_lng = {s[0] for s in self.instance.languages.all().values_list('id')}
        new_lng = {s.id for s in Language.objects.filter(id__in=self.validated_data['languageslist'])}
        if current_lng != new_lng:
            changes['languages'] = list(new_lng)

        if changes:
            self.instance.tmp_changes = changes
            self.instance.profile_status = User.PossibleState.PENDING_APPROVAL
            return self.instance.save()

        return self.instance


class ProfileAdminValidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_status']

    def validate_profile_status(self, val):
        if self.instance.profile_status != User.PossibleState.PENDING_APPROVAL:
            raise serializers.ValidationError({'profile_status': 'Profile already approved'})
        if val == self.instance.profile_status:
            raise serializers.ValidationError({'profile_status': 'You should change status to store it.'})

        return val

    def save(self, **kwargs):

        ProfileChanges.objects.create(
            change_time=datetime.timezone,
            user=self.instance,
            changes=self.instance.tmp_changes,
            prev_state=self.instance.profile_status,
            next_state=self.validated_data['profile_status']
        )

        if self.validated_data['profile_status'] == User.PossibleState.APPROVED:
            for attr in self.instance.tmp_changes:
                # Store foreign key
                if type(getattr(self.instance.__class__, attr)) is models.fields.related_descriptors.ForwardManyToOneDescriptor:
                    try:
                        model = getattr(self.instance.__class__, attr)
                        val = model.get_queryset().get(pk=self.instance.tmp_changes[attr])
                        field = getattr(self.instance, attr)
                        setattr(self.instance, attr, val)
                    except:
                        raise serializers.ValidationError({attr: 'Invalid value'})
                #store many2many
                elif type(getattr(self.instance.__class__, attr)) is models.fields.related_descriptors.ManyToManyDescriptor:
                    field = getattr(self.instance, attr)
                    field.clear()
                    for id in self.instance.tmp_changes[attr]:
                        field.add(id)
                else:
                    setattr(self.instance, attr, self.instance.tmp_changes[attr])


            self.instance.profile_status = User.PossibleState.APPROVED
            self.instance.tmp_changes = {}
            return self.instance.save()

        else:
            self.instance.profile_status = self.validated_data['profile_status']
            return self.instance.save()


class ShortViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'modify_time', 'username', 'profile_status']
        extra_kwargs = {
            'profile_status': {'read_only': True, }
        }


class TutorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'max_cost', 'specialities', 'languages']


class TutorSearchViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = TutorsSerializer
    queryset = User.objects.filter(tutor=True, profile_status=User.PossibleState.APPROVED)


class RegisterViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class ProfileViewSet(mixins.CreateModelMixin, GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        instance = self.request.user
        serializer = self.get_serializer(instance, data=request.data, )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.request.user, many=False)
        return Response(serializer.data)


class AdminViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = ShortViewSerializer
    queryset = User.objects.filter(is_superuser=False)

    def get_queryset(self):
        if self.request.query_params.get('profile_status'):
            return self.queryset.filter(profile_status=self.request.query_params.get('profile_status'))
        return self.queryset

    def get_serializer_class(self):
        if self.request.method == 'GET' and 'pk' in self.kwargs:
            return ProfileSerializer
        if self.request.method == 'PUT' and 'pk' in self.kwargs:
            print("update")
            return ProfileAdminValidateSerializer
        return ShortViewSerializer
