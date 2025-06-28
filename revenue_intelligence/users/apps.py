import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "revenue_intelligence.users"
    verbose_name = _("Users")

    def ready(self):
        with contextlib.suppress(ImportError):
            import revenue_intelligence.users.signals  # noqa: F401, PLC0415
