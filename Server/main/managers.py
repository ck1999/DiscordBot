from django.contrib.auth import models
from django.contrib.auth.models import PermissionsMixin

class DiscordOAuthManager(models.UserManager):
    def create_new(self, user):
        __tag = '{}#{}'.format(user.get('username'), user.get('discriminator'))
        __user = self.create(
            user_id=user.get('id'),
            avatar=user.get('avatar'),
            public_flags=user.get('public_flags'),
            flags=user.get('flags'),
            locale=user.get('locale'),
            mfa_enabled=user.get('mfa_enabled'),
            tag=__tag,
            is_active=False 
        )   
        return __user