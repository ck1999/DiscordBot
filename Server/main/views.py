from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login
import requests
from .models import BlackList, DiscordGuild, DiscordUser, DiscordUserInGuild, BotSettings
from .serializers import BlackListSerializer, DiscordUserSerializer, DiscordGuildSerializer, DiscordUserInGuildSerializer, BotSettingsSerializer
from .data import API_ENDPOINT, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, DISCORD_OAUTH
from asgiref.sync import sync_to_async
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@sync_to_async
class SettingsAPI():

    class ListView(APIView):
        serializer_class = BotSettingsSerializer

        def get(self, request):
            settings = BotSettings.objects.all()
            serializer = self.serializer_class(settings, many=True)
            return Response(serializer.data, status=200)

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    class OneView(APIView):
        serializer_class = BotSettingsSerializer

        def get(self, request, pk):
            user = get_object_or_404(BotSettings, pk=pk)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=200)

        def put(self, request, pk):
            guild = get_object_or_404(BotSettings, pk=pk) 
            serializer = self.serializer_class(guild, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

@sync_to_async
class DiscordUsersAPI():

    class ListView(APIView):
        serializer_class = DiscordUserSerializer

        def get(self, request):
            users = DiscordUser.objects.all()
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data, status=200)

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    class OneView(APIView):
        serializer_class = DiscordUserSerializer

        def get(self, request, pk):
            user = get_object_or_404(DiscordUser, pk=pk)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=200)

        def put(self, request, pk):
            guild = get_object_or_404(DiscordUser, pk=pk) 
            serializer = self.serializer_class(guild, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

@sync_to_async
class DiscordGuildsAPI():

    class ListView(APIView):
        serializer_class = DiscordGuildSerializer

        def get(self, request):
            guilds = DiscordGuild.objects.all()
            serializer = self.serializer_class(guilds, many=True)
            return Response(serializer.data, status=200)

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    class OneView(APIView):
        serializer_class = DiscordGuildSerializer

        @method_decorator(cache_page(60*60*8))
        def get(self, request, pk):
            guild = get_object_or_404(DiscordGuild, pk=pk)
            serializer = self.serializer_class(guild)
            return Response(serializer.data, status=200)

        def put(self, request, pk):
            guild = get_object_or_404(DiscordGuild, pk=pk) 
            serializer = self.serializer_class(guild, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

@sync_to_async
class DiscordUsersInGuildsAPI():

    class ListView(APIView):
        serializer_class = DiscordUserInGuildSerializer

        def get(self, request, gk):
            guild = DiscordGuild.objects.get(guild_id=gk)
            users = DiscordUserInGuild.objects.filter(guild=guild)
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data, status=200)

        def post(self, request, gk):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    class OneView(APIView):
        serializer_class = DiscordUserInGuildSerializer

        def get(self, request, gk, uk):
            guild = DiscordGuild.objects.get(guild_id=gk)
            instance = DiscordUserInGuild.objects.get(guild=guild, user=uk)
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=200)

        def put(self, request, gk, uk):
            guild = get_object_or_404(DiscordGuild, guild_id=gk)
            instance = DiscordUserInGuild.objects.get(guild=guild, user=uk)
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

@sync_to_async
class BlacklistedUsers():

    class ListView(APIView):
        serializer_class = BlackListSerializer

        @method_decorator(cache_page(60*60*12))
        def get(self, request):
            users = BlackList.objects.all()
            serializer = self.serializer_class(users, many=True)
            return Response(serializer.data, status=200)

        def post(self, request):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

    class OneView(APIView):
        serializer_class = BlackListSerializer

        def get(self, request, pk):
            user = get_object_or_404(BlackList, pk=pk)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=200)

        def put(self, request, pk):
            user = get_object_or_404(BlackList, pk=pk) 
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)

        def delete(self, request, pk):
            user = get_object_or_404(BlackList, pk=pk)
            serializer = self.serializer_class(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.delete(user)
                return Response(status=204)
            return Response(serializer.errors, status=400)

class IndexPage(View):

    def get(self, request):
        print(request.user)
        return render(request, 'index.html')

class OAuth_Discord():

    class DiscordAuth(View):
        
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.redirect_url = DISCORD_OAUTH

        def get(self, request):
            return redirect(self.redirect_url)

    class DiscordGate(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'index.html'

        def get_data(self, code):
            data = {
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI
            }
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.post(f'{API_ENDPOINT}/oauth2/token', data=data, headers=headers)
            token = response.json().get('access_token')
            response = requests.get(f"{API_ENDPOINT}/users/@me", headers={
                'Authorization': f'Bearer {token}'
            })
            return response.json()

        def get(self, request):
            code = request.GET.get('code')
            try:
                user = authenticate(request, user=self.get_data(code))
                user = list(user).pop()
                login(request, user)
            except:
                pass
            return render(request, self.template_name)

class DiscordUsers():

    class ListView(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'admin/users.html'
            self.error_template = '404.html'

        def get(self, request):
            if not request.user.is_staff:
                return render(request, self.error_template)
            query = DiscordUser.objects.all()
            context = {
                'users': query
            }
            return render(request, self.template_name, context)

    class OneView(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'admin/user.html'
            self.error_template = '404.html'

        def get(self, request, pk):
            user = get_object_or_404(DiscordUser, user_id=pk)
            if not request.user.is_staff and request.user != user:
                return render(request, self.error_template)
            guilds = DiscordUserInGuild.objects.filter(user=user)
            context = {
                'user': user,
                'guilds': guilds
            }
            return render(request, self.template_name, context)

class DiscordGuilds():

    class ListView(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'admin/guilds.html'
            self.error_template = '404.html'

        def get(self, request):
            if not request.user.is_staff:
                return render(request, self.error_template)
            query = DiscordGuild.objects.all()
            context = {
                'guilds': query
            }
            return render(request, self.template_name, context)

    class OneView(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'admin/guild.html'
            self.error_template = '404.html'

        def get(self, request, pk):
            guild = get_object_or_404(DiscordGuild, guild_id=pk)
            if not request.user.is_staff:
                return render(request, self.error_template)
            users = DiscordUserInGuild.objects.filter(guild=guild)
            context = {
                'guild': guild,
                'users': users
            }
            return render(request, self.template_name, context)

class Settings():

    class OneView(View):

        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)
            self.template_name = 'admin/settings.html'
            self.error_template = '404.html'

        def get(self, request):
            if not request.user.is_staff:
                return render(request, self.error_template)
            settings = get_object_or_404(BotSettings, id=1)
            context = {
                'settings': settings
            }
            return render(request, self.template_name, context)