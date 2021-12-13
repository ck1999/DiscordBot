from django.db import models
from .managers import DiscordOAuthManager

class DiscordUser(models.Model):

    objects = DiscordOAuthManager()

    user_id = models.CharField(verbose_name='User ID', max_length=50, unique=True, primary_key=True, null=False, blank=False)
    username = models.CharField(verbose_name='Nickname', max_length=50)
    tag = models.CharField(verbose_name='Tag', max_length=50)
    avatar = models.CharField(verbose_name='Avatar', max_length=100)
    public_flags = models.IntegerField()
    flags = models.IntegerField()
    locale = models.CharField(max_length=100)
    mfa_enabled = models.BooleanField()
    last_login = models.DateTimeField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.user_id

    def is_authenticated(self, request):
        return True

    @property
    def is_admin(self):
        return self.is_staff

    def has_perm(self, perm, obj=None):
       return self.is_staff

    def has_module_perms(self, app_label):
       return self.is_staff

    def get_username(self):
        return self.username

class DiscordGuild(models.Model):
    guild_id = models.CharField(verbose_name='Guild ID', max_length=50, unique=True, primary_key=True, null=False, blank=False)
    name = models.CharField(verbose_name='Guild name', max_length=50)
    setting_plugin_admin = models.BooleanField(verbose_name='Модераторство')
    setting_plugin_rank = models.BooleanField(verbose_name='Система рангов')
    setting_plugin_economy = models.BooleanField(verbose_name='Экономика')
    setting_plugin_games = models.BooleanField(verbose_name='Игры')
    setting_plugin_birthday = models.BooleanField(verbose_name='Дни Рождения')
    setting_plugin_music = models.BooleanField(verbose_name='Музыка')
    log_channel = models.CharField(verbose_name='Log channel', max_length=50, null=True, blank=True)
    prefix = models.CharField(verbose_name='Префикс', max_length=2)

    def __str__(self) -> str:
        return self.guild_id

class DiscordUserInGuild(models.Model):
    guild = models.ForeignKey(DiscordGuild, verbose_name='Guild', on_delete=models.CASCADE)
    user = models.CharField(verbose_name='User ID', max_length=50, null=False, blank=False)
    balance = models.IntegerField(verbose_name='Баланс', default=100)
    exp = models.IntegerField(verbose_name='Опыт', default=0)
    level = models.IntegerField(verbose_name='Уровень', default=1)
    xp_time_lock = models.FloatField(verbose_name='EXP_TIME_LOCK')
    birthday = models.DateField(verbose_name='Время Дня Рождения', null=True, blank=True)
    bank = models.IntegerField(verbose_name='Банк', default=0)

    class Meta:
        unique_together = (("guild", "user"),)

class BotSettings(models.Model):
    token = models.CharField(verbose_name='Token', max_length=100)
    log = models.CharField(verbose_name='Log channel', max_length=100)
    cooldown_classic = models.IntegerField(verbose_name='Cooldown Classic')
    cooldown_medium = models.IntegerField(verbose_name='Cooldown Medium')
    cooldown_large = models.IntegerField(verbose_name='Cooldown Large')
    cooldown_day = models.IntegerField(verbose_name='Cooldown Extra')
    sleep = models.IntegerField(verbose_name='Sleep Time')

class BlackList(models.Model):
    user = models.CharField(verbose_name='User ID', max_length=50, unique=True, primary_key=True, null=False, blank=False)
    reason = models.CharField(verbose_name='Reason', max_length=100, default='No reason')

    def __str__(self) -> str:
        return self.user