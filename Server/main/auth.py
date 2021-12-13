from django.contrib.auth.backends import BaseBackend
from .models import DiscordUser

class DiscordOAuthBackend(BaseBackend):
    def authenticate(self, request, user) -> DiscordUser:
        __user = DiscordUser.objects.filter(user_id=user['id'])
        if not __user:
            __user = DiscordUser.objects.create_new(user)   
        return __user

    def get_user(self, id):
        try:
            return DiscordUser.objects.get(user_id=id)
        except DiscordUser.DoesNotExist:
            return None