from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = 'checkout'

    def ready(self):
        # Import signals to ensure they are registered
        import checkout.signals
