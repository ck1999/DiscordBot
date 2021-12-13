from spotipy import Spotify as Sp
from spotipy.oauth2 import SpotifyClientCredentials
from cogs.settings import SPOTIFY_CLIENT_ID, SPOTIFY_SECRET

spotify = Sp(auth_manager=SpotifyClientCredentials(client_id = SPOTIFY_CLIENT_ID, client_secret = SPOTIFY_SECRET))

def get_tracks(type: str, link: str) -> list:
    tracks = []
    if type == 'track':
        response = spotify.track(link)
        _name = response.get('name') + ' ' + response.get('artists')[0].get('name') + ' песня'
        tracks.append(_name)
        return tracks
    elif type == 'playlist':
        response = spotify.playlist_tracks(link)
        for i in response.get('items'):
            track = i.get('track')
            _name = track.get('name') + ' ' + track.get('artists')[0].get('name') + ' песня'
            tracks.append(_name)
        return tracks
    else:
        response = spotify.album_tracks(link)
        for i in response.get('items'):
            _name = i.get('name') + ' ' + i.get('artists')[0].get('name') + ' песня'
            tracks.append(_name)
        return tracks