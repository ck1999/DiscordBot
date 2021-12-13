from django.db.models import fields
from rest_framework import serializers, settings
from .models import BlackList, DiscordGuild, DiscordUser, DiscordUserInGuild, BotSettings

class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = '__all__'

    def create(self, validated_data):

        user = DiscordUser(**validated_data)
        user.save()

        return user

class DiscordGuildSerializer(serializers.ModelSerializer):
    setting_plugin_admin = serializers.BooleanField(default=False)
    setting_plugin_rank = serializers.BooleanField(default=False)
    setting_plugin_economy = serializers.BooleanField(default=False)
    setting_plugin_games = serializers.BooleanField(default=False)
    setting_plugin_birthday = serializers.BooleanField(default=False)
    setting_plugin_music = serializers.BooleanField(default=False)
    class Meta:
        model = DiscordGuild
        fields = '__all__'

    def create(self, validated_data):

        guild = DiscordGuild(**validated_data)
        guild.save()

        return guild

    def update(self, instance, validated_data):
        instance.setting_plugin_admin = False
        instance.setting_plugin_rank = False
        instance.setting_plugin_economy = False
        instance.setting_plugin_games = False
        instance.setting_plugin_birthday = False
        instance.setting_plugin_music = False
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class DiscordUserInGuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUserInGuild
        fields = '__all__'

    def create(self, validated_data):
        user = DiscordUserInGuild(**validated_data)
        user.save()

        return user 

    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class BotSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotSettings
        fields = '__all__'

    def create(self, validated_data):
        settings = BotSettings(**validated_data)
        settings.save()

        return settings
    
    def update(self, instance, validated_data):
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

class BlackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackList
        fields = '__all__'

    def create(self, validated_data):
        user = BlackList(**validated_data)
        user.save()

        return user

    def delete(self, instance):
        instance.delete()
        return None