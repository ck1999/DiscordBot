import requests
data = requests.get('http://127.0.0.1:8000/api/settings/1').json()

settings = {
    'token': data.get('token'),
    'api': 'http://127.0.0.1:8000/api/',
    'log': data.get('log'),
    'ticket': 0,
    'cooldown_classic': data.get('cooldown_classic'),
    'cooldown_medium': data.get('cooldown_medium'),
    'cooldown_large': data.get('cooldown_large'),
    'cooldown_day': data.get('cooldown_day'),
    'sleep': data.get('sleep')
}

# admins = {
#     'owner':
# }
spotify_settings = {
    #Provide here your data
}

ytdl_format_options = {
    "format" : "bestaudio", 
    "quiet" : True
}

def setup(bot):
    pass