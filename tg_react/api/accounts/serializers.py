import json
import base64
import phonenumbers

from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext as _

from tg_react.settings import exclude_fields_from_user_details, get_user_signup_fields


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [f.name for f in get_user_model()._meta.fields if f.name not in exclude_fields_from_user_details()]

        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'is_active': {'read_only': True},
            'date_joined': {'read_only': True},
        }


class AuthenticationSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def validate(self, data):
        credentials = {
            'email': data.get('email', None),
            'password': data.get('password', None)
        }

        if all(credentials.values()):
            from django.contrib.auth import authenticate
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError('Your account has been disabled')

                self.user = user
                # hide the password so it wont leak
                credentials['password'] = '-rr-'

                return credentials

            else:
                raise serializers.ValidationError('Unable to login with provided credentials.')
        else:
            raise serializers.ValidationError('Enter both email and password')

    def create(self, validated_data):
        return validated_data


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fields_we_do_not_want = [
            'id', 'email', 'password', 'is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
        important_signup_fields = get_user_signup_fields()
        model = get_user_model()
        # Using ModelSerializers model field to serializer field mapper
        # to build missing fields for signup serializer
        mapping = ClassLookupDict(serializers.ModelSerializer.serializer_field_mapping)
        for model_field in model._meta.fields:
            if model_field.name in important_signup_fields and model_field.name not in fields_we_do_not_want:
                self._declared_fields[model_field.name] = mapping[model_field](required=True)

    def validate_email(self, data):
        u = self.context['request'].user
        if u.is_authenticated() and data == u.email:
            return data
        else:
            if get_user_model().objects.filter(email=data).exists():
                raise serializers.ValidationError(_("User with this e-mail address already exists"))
        return data

    def validate_phone(self, data):
        try:
            nr = phonenumbers.parse(data, None)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise serializers.ValidationError(_("Phone number needs to include valid country code (E.g +37255555555)"))
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def validate_email(self, email):
        user_model = get_user_model()

        try:
            self.user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            raise serializers.ValidationError(_("We do not have user with given e-mail address in our system"))

        return email

    def validate(self, data):
        # Serialize uid and token to json then encode to base64
        # Feauters:
        # one parameter for api insted two (uid and token)
        uid_and_token = json.dumps({
          'uid': self.user.pk,
          'token': default_token_generator.make_token(self.user)
        }).encode('utf-8')
        return {'uid_and_token_b64': base64.urlsafe_b64encode(uid_and_token).decode('ascii')}


class RecoveryPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    # uid_and_token receive json dict encoded with base64
    uid_and_token_b64 = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def validate(self, data):

        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(_("Password mismatch."))

        return {'password': data['password']}

    def validate_uid_and_token_b64(self, uid_and_token_b64):

        try:
            # Deserealize data from json
            json_data = base64.urlsafe_b64decode(uid_and_token_b64).decode('utf-8')
            data = json.loads(json_data)
        except:
            raise serializers.ValidationError(_("Broken data."))

        uid = data.get('uid', None)
        token = data.get('token', None)

        try:
            assert uid and token and isinstance(uid, int)
        except AssertionError:
            raise serializers.ValidationError(_("Broken data."))

        user_model = get_user_model()

        try:
            self.user = user_model.objects.get(pk=uid)
        except user_model.DoesNotExist:
            raise serializers.ValidationError(_("User not found."))

        # validate token
        if not default_token_generator.check_token(self.user, token):
            msg = "%s %s" % (_("This password recovery link has expired or associated user does not exist."), 
                             _("Use password recovery form to get new e-mail with new link."))
            raise serializers.ValidationError(msg)
