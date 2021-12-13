"""DiscordBot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from main.views import DiscordUsersAPI, DiscordGuildsAPI, DiscordUsersInGuildsAPI, OAuth_Discord, IndexPage, DiscordUsers, DiscordGuilds, SettingsAPI, Settings, BlacklistedUsers

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', DiscordUsersAPI.ListView.as_view()),
    path('api/users/<int:pk>', DiscordUsersAPI.OneView.as_view()),
    path('api/guilds', DiscordGuildsAPI.ListView.as_view()),
    path('api/guilds/<int:pk>', DiscordGuildsAPI.OneView.as_view()),
    path('api/<int:gk>', DiscordUsersInGuildsAPI.ListView.as_view()),
    path('api/<int:gk>/<int:uk>', DiscordUsersInGuildsAPI.OneView.as_view()),
    path('api/settings', SettingsAPI.ListView.as_view()),
    path('api/settings/<int:pk>', SettingsAPI.OneView.as_view()),
    path('bot/settings', Settings.OneView.as_view()),
    path('login', OAuth_Discord.DiscordAuth.as_view()),
    path('', OAuth_Discord.DiscordGate.as_view(), name='index'),
    path('menu', IndexPage.as_view(), name=''),
    path('users', DiscordUsers.ListView.as_view(), name='users'),
    path('user/<int:pk>', DiscordUsers.OneView.as_view(), name='user'),
    path('guilds', DiscordGuilds.ListView.as_view(), name='guilds'),
    path('guild/<int:pk>', DiscordGuilds.OneView.as_view(), name='guild'),
    path('api/blacklist', BlacklistedUsers.ListView.as_view(), name='blacklist'),
    path('api/blacklist/<int:pk>', BlacklistedUsers.OneView.as_view())
]
