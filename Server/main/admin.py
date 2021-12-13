from django.contrib import admin
from .models import DiscordGuild, DiscordUser, DiscordUserInGuild

# Register your models here.
admin.site.register(DiscordGuild)
admin.site.register(DiscordUser)
admin.site.register(DiscordUserInGuild)