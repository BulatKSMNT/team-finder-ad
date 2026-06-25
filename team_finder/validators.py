from urllib.parse import urlparse

from django.core.exceptions import ValidationError

from .constants import GITHUB_ALLOWED_HOSTS


def validate_github_url(github_url):
    if not github_url:
        return github_url

    parsed_url = urlparse(github_url)
    host = parsed_url.netloc.lower()

    if host not in GITHUB_ALLOWED_HOSTS:
        raise ValidationError("Ссылка должна вести на GitHub.")

    return github_url
