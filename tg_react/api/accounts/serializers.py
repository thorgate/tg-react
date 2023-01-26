import json
import base64

from rest_framework import serializers
from rest_framework.utils.field_mapping import ClassLookupDict

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import gettext as _

from tg_react.settings import (
    exclude_fields_from_user_details,
    get_user_signup_fields,
    get_email_case_sensitive,
    get_user_extra_fields,
)


class UserDetailsSerializer(serializers.ModelSerializer):
    # Overriding default field to get rid of existing uniquevalidator
    # because i want to show better validation message (see validate_email below)
    email = serializers.EmailField(validators=[])

    class Meta:
        model = get_user_model()
        fields = [
            f.name
            for f in get_user_model()._meta.fields
            if f.name not in exclude_fields_from_user_details()
        ]

        extra_kwargs = {
            "password": {"write_only": True},
            "id": {"read_only": True},
            "is_active": {"read_only": True},
            "is_staff": {"read_only": True},
            "is_superuser": {"read_only": True},
            "date_joined": {"read_only": True},
            "last_login": {"read_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in exclude_fields_from_user_details():
            if field in self.fields:
                del self.fields[field]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if not get_email_case_sensitive():
            email = data and data.get("email")
            if email:
                data["email"] = email.lower()

        return data

    def validate_email(self, data):
        current_email = self.instance.email

        if not get_email_case_sensitive():
            data = data.lower()
            current_email = current_email.lower()

        if (
            get_user_model().objects.filter(email=data).exists()
            and current_email != data
        ):
            raise serializers.ValidationError(
                _("User with this e-mail address already exists.")
            )

        return data

    def get_fields(self):
        static_fields = super().get_fields()

        for name, cfg in get_user_extra_fields().items():
            static_fields[name] = cfg[0](**cfg[1])

        return static_fields


class AuthenticationSerializer(serializers.Serializer):
    password = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[get_user_model().USERNAME_FIELD] = serializers.CharField()

        self.user = None

    def validate(self, attrs):
        credentials = {"password": attrs.get("password", None)}

        username_field = get_user_model().USERNAME_FIELD
        credentials[username_field] = attrs.get(username_field, None)

        if all(credentials.values()):
            from django.contrib.auth import authenticate  # NOQA

            if username_field == "email":
                if not get_email_case_sensitive():
                    credentials[username_field] = credentials[username_field].lower()

            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    raise serializers.ValidationError(
                        _("Your account has been disabled.")
                    )

                self.user = user
                # hide the password so it wont leak
                credentials["password"] = "-rr-"

                return credentials

            raise serializers.ValidationError(
                _("Unable to login with provided credentials.")
            )

        raise serializers.ValidationError(_("Please enter both email and password."))

    def create(self, validated_data):
        return validated_data


def phonenumber_validation(data):
    """Validates phonenumber

    Similar to phonenumber_field.validators.validate_international_phonenumber() but uses a different message if the
    country prefix is absent.
    """
    from phonenumber_field.phonenumber import to_python  # NOQA

    phone_number = to_python(data)
    if not phone_number:
        return data

    if not phone_number.country_code:
        raise serializers.ValidationError(
            _("Phone number needs to include valid country code (E.g +37255555555).")
        )

    if not phone_number.is_valid():
        raise serializers.ValidationError(_("The phone number entered is not valid."))

    return data


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fields_we_do_not_want = [
            "id",
            "email",
            "password",
            "is_staff",
            "is_superuser",
            "is_active",
            "date_joined",
            "last_login",
        ]
        important_signup_fields = get_user_signup_fields()
        model = get_user_model()
        # Using ModelSerializers model field to serializer field mapper
        # to build missing fields for signup serializer
        original_mapping = serializers.ModelSerializer.serializer_field_mapping

        try:
            from phonenumber_field.modelfields import PhoneNumberField  # NOQA

            original_mapping.update({PhoneNumberField: serializers.CharField})
        except ImportError:
            pass

        mapping = ClassLookupDict(original_mapping)
        for model_field in model._meta.fields:
            if (
                model_field.name in important_signup_fields
                and model_field.name not in fields_we_do_not_want
            ):
                field_kwargs = {"required": True}
                if "phone" in model_field.name:
                    field_kwargs["validators"] = [phonenumber_validation]
                self._declared_fields[model_field.name] = mapping[model_field](
                    **field_kwargs
                )

    def validate_email(self, data):
        if not get_email_case_sensitive():
            data = data.lower()

        if get_user_model().objects.filter(email=data).exists():
            raise serializers.ValidationError(
                _("User with this e-mail address already exists.")
            )

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def validate_email(self, email):
        user_model = get_user_model()

        if not get_email_case_sensitive():
            email = email.lower()

        try:
            self.user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            raise serializers.ValidationError(
                _("We do not have user with given e-mail address in our system.")
            )

        return email

    def validate(self, attrs):
        # Serialize uid and token to json then encode to base64
        uid_and_token = json.dumps(
            {
                "uid": self.user.pk,
                "token": default_token_generator.make_token(self.user),
            }
        ).encode("utf-8")
        return {
            "uid_and_token_b64": base64.urlsafe_b64encode(uid_and_token).decode("ascii")
        }


class RecoveryPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    password_confirm = serializers.CharField(required=True)

    # uid_and_token receive json dict encoded with base64
    uid_and_token_b64 = serializers.CharField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = None

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(_("Password mismatch."))

        return {"password": attrs["password"]}

    def validate_uid_and_token_b64(self, uid_and_token_b64):

        try:
            # Deserialize data from json
            json_data = base64.urlsafe_b64decode(uid_and_token_b64).decode("utf-8")
            data = json.loads(json_data)
        except Exception:
            raise serializers.ValidationError(_("Broken data."))

        uid = data.get("uid", None)
        token = data.get("token", None)

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
            msg_0 = _(
                "This password recovery link has expired or associated user does not exist."
            )
            msg_1 = _("Use password recovery form to get new e-mail with new link.")

            raise serializers.ValidationError(f"{msg_0} {msg_1}")


class LanguageCodeSerializer(serializers.Serializer):
    language_code = serializers.ChoiceField(choices=settings.LANGUAGES, required=True)
