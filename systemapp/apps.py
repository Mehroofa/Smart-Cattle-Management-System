from django.apps import AppConfig


class SystemappConfig(AppConfig):
    name = 'systemapp'
def ready(self):
    import systemapp.signals
