from django.apps import AppConfig


class BillsConfig(AppConfig):
    name = 'bills'

    def ready(self):
        import bills.signals