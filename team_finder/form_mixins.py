from .validators import validate_github_url


class GithubUrlValidationMixin:
    github_url_field_name = "github_url"

    def clean_github_url(self):
        github_url = self.cleaned_data.get(self.github_url_field_name, "")

        return validate_github_url(github_url)
