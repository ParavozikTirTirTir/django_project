from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StaffConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff'
    verbose_name = _('Мастера и услуги')

    def ready(self):
        # Заготовка под сигналы (например: уведомление при добавлении нового мастера)
        # from . import signals
        pass
