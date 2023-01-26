import pytest

# Accept-Language


@pytest.mark.parametrize(
    "language_code,expected",
    [
        (None, "en"),
        ("en", "en"),
        ("et", "et"),
        ("ru", "ru"),
        ("no", "en"),
    ],
)
def test_locale_middleware(client, language_code, expected):
    extras = {}
    if language_code:
        extras["HTTP_ACCEPT_LANGUAGE"] = language_code

    response = client.get("/test-language/", **extras)

    assert response.content.decode() == f"current_language: {expected}"
