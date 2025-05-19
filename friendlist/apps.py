from django.apps import AppConfig


class FriendlistConfig(AppConfig):
    name = "friendlist"

    def ready(self):
        import friendlist.signals
