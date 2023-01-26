from copy import copy
from unittest.mock import patch, ANY

import pytest

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from model_bakery import baker
from rest_framework.fields import CharField
from rest_framework.test import APIClient

from tg_react.settings import (
    get_user_extra_fields,
    configure,
    exclude_fields_from_user_details,
)


@pytest.fixture(scope="function")
def api_client():
    return APIClient()


@pytest.fixture(scope="function")
def user():
    user = baker.make(User, is_staff=False)
    user.set_password("test")
    user.save()

    return user


@pytest.fixture(scope="function")
def user_with_email():
    user = baker.make(User, is_staff=False, email="foO@BAr.baz")
    user.set_password("test")
    user.save()

    return user


@pytest.fixture(scope="function")
def test_user_json(user):
    return {
        "id": user.pk,
        "date_joined": user.date_joined.isoformat().replace("+00:00", "Z"),
        "is_staff": user.is_staff,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "last_login": user.last_login.isoformat().replace("+00:00", "Z"),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "username": user.username,
    }


@pytest.fixture(scope="function")
def user_api_client(api_client, user):
    api_client.force_login(user)
    return api_client


@pytest.mark.django_db
def test_accounts_user_page_not_authorized(api_client):
    # User profile not authorized if not logged in
    response = api_client.get(reverse("api-user-details"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_accounts_user_page_authorized(user_api_client, user, test_user_json):
    response = user_api_client.get(reverse("api-user-details"))
    assert response.status_code == 200
    assert response.json() == test_user_json


@pytest.mark.django_db
def test_accounts_user_exclude_fields(user_api_client, user, test_user_json, settings):
    test_user_json = copy(test_user_json)

    excluded = ["is_active", "is_staff", "username"]

    for k in excluded:
        del test_user_json[k]

    settings.TGR_EXCLUDED_USER_FIELDS = excluded
    configure()

    assert exclude_fields_from_user_details() == excluded

    response = user_api_client.get(reverse("api-user-details"))
    assert response.status_code == 200
    assert response.json() == test_user_json


@pytest.mark.django_db
def test_user_extra_fields(settings):
    with pytest.raises(ImproperlyConfigured) as exc_info:
        settings.TGR_USER_EXTRA_FIELDS = []
        get_user_extra_fields(validate=True)

    assert "TGR_USER_EXTRA_FIELDS must be a dict" in str(exc_info.value)

    with pytest.raises(ImproperlyConfigured) as exc_info:
        settings.TGR_USER_EXTRA_FIELDS = {
            "yolo": False,
        }
        get_user_extra_fields(validate=True)

    assert (
        "TGR_USER_EXTRA_FIELDS value must be a module path or list[path, kwargs]"
        in str(exc_info.value)
    )

    with pytest.raises(ImproperlyConfigured) as exc_info:
        settings.TGR_USER_EXTRA_FIELDS = {
            "yolo": {},
        }
        get_user_extra_fields(validate=True)

    assert (
        "TGR_USER_EXTRA_FIELDS value must be a module path or list[path, kwargs]"
        in str(exc_info.value)
    )

    settings.TGR_USER_EXTRA_FIELDS = {
        "yolo": "rest_framework.fields.CharField",
    }
    extra_fields = get_user_extra_fields(validate=True)

    assert extra_fields == {
        "yolo": [CharField, {}],
    }


@pytest.mark.django_db
def test_get_extra_fields(settings, user_api_client, user):
    settings.TGR_USER_EXTRA_FIELDS = {
        "yolo": [
            "rest_framework.fields.CharField",
            {"source": "pk", "read_only": True},
        ],
    }
    configure()

    response = user_api_client.get(reverse("api-user-details"))
    assert response.status_code == 200

    data = response.json()

    assert "yolo" in data
    assert data["yolo"] == str(user.pk)


@pytest.mark.django_db
def test_accounts_user_email_case_sensitive(settings, api_client, user_with_email):
    api_client.force_login(user_with_email)

    response = api_client.get(reverse("api-user-details"))
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == user_with_email.email

    settings.TGR_EMAIL_CASE_SENSITIVE = False
    configure()

    response = api_client.get(reverse("api-user-details"))
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == user_with_email.email.lower()

    settings.TGR_EMAIL_CASE_SENSITIVE = True
    configure()

    response = api_client.get(reverse("api-user-details"))
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == user_with_email.email


@pytest.mark.django_db
def test_accounts_login(api_client, user):
    response = api_client.get(reverse("api-user-login"))
    assert response.status_code == 405

    response = api_client.post(
        reverse("api-user-login"), data={"username": user.username, "password": "test"}
    )
    assert response.status_code == 200

    assert response.json() == {"success": True}


@pytest.mark.django_db
def test_accounts_login_error(api_client, user):
    response = api_client.get(reverse("api-user-login"))
    assert response.status_code == 405

    response = api_client.post(
        reverse("api-user-login"),
        data={"username": user.username, "password": "asdasds"},
    )
    assert response.status_code == 400

    assert response.json() == {
        "errors": {"non_field_errors": ["Unable to login with provided credentials."]}
    }


@pytest.mark.django_db
def test_post_login_handler(api_client, user, settings):
    settings.TGR_POST_LOGIN_HANDLER = "example.handlers.post_login"
    configure()

    with patch("example.handlers.post_login") as mock:
        response = api_client.post(
            reverse("api-user-login"),
            data={"username": user.username, "password": "test"},
        )
        assert response.status_code == 200

        mock.assert_called_once_with(user=user, request=ANY, old_session=ANY)


@pytest.mark.django_db
def test_accounts_logout(user_api_client, api_client, user):
    response = api_client.get(reverse("api-user-logout"))
    assert response.status_code == 405

    response = api_client.post(reverse("api-user-logout"), data={})
    assert response.status_code == 200

    assert response.json() == {"success": True}

    # logout only works when authenticated
    response = api_client.post(reverse("api-user-logout"), data={})
    assert response.status_code == 403


@pytest.mark.django_db
def test_post_logout_handler(user_api_client, user, settings):
    settings.TGR_POST_LOGOUT_HANDLER = "example.handlers.post_logout"
    configure()

    with patch("example.handlers.post_logout") as mock:
        response = user_api_client.post(reverse("api-user-logout"), data={})
        assert response.status_code == 200

        mock.assert_called_once_with(user=user, request=ANY, old_session=ANY)
