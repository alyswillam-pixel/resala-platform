from django.apps import AppConfig


class CommitteesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "resala_platform.committees"

    def ready(self):
        from . import signals  # noqa: F401
