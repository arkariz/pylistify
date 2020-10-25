from django.db import models
import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth

artist_id = []
track_id = []
danceability = []
energy = []
tempo = []
loudness = []
recommendations_track_id = []
scope = 'user-library-read user-library-modify user-read-recently-played playlist-modify-private playlist-read-collaborative playlist-read-private playlist-modify-public'
cliend_id = '080e4d9856d645c396e08ec0b1088a02'
client_secret = '26b9fef0e6fc4b11a77618ba41e9cd20'
Uri = 'https://elopakala.herokuapp.com/addplaylist/'


sp = spotipy.Spotify(auth_manager=SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope))

def getRecentTrack():
    artist_name = []
    track_name =[]

    # Get Artist Id and track id
    recent_track = sp.current_user_recently_played(limit=5)
    for idx, item in enumerate(recent_track['items']):
        track = item['track']

        artist_name.append(track['artists'][0]['name'])
        track_name.append(track['name'])

        # print(idx, track['artists'][0]['name'], " – ", track['name'])

        track_feature = track['id']
        track_id.append(track_feature)

        artist = track['artists'][0]['id']
        artist_id.append(artist)

    # Get track Attribute
    for item_id in track_id:
        audio_features = sp.audio_features(tracks=item_id)
        for idx, item in enumerate(audio_features):
            danceability.append(item['danceability'])
            energy.append(item['energy'])
            tempo.append(item['tempo'])
            loudness.append(item['loudness'])
    content = {
        'artist':artist_name,
        'track_name': track_name
    }
    return content

# Get recommendation track based on artists and attribute
def getRecommendationsTrack():
    artist_name = []
    track_name = []
    recommendations = sp.recommendations(seed_artists=artist_id, min_danceability=min(danceability),
                                         max_danceability=max(danceability), min_tempo=min(tempo),
                                         max_tempo=max(tempo), min_energy=min(energy), max_energy=max(energy),
                                         min_loudness=min(loudness))

    for idx, item in enumerate(recommendations['tracks']):
        # print(idx, item['artists'][0]['name'], " – ", item['name'])
        artist_name.append(item['artists'][0]['name'])
        track_name.append(item['name'])
        track_id = item['id']
        recommendations_track_id.append(track_id)

    content = {
        'artist': artist_name,
        'track_name': track_name
    }
    return content

def playlist(playlist_name):
    # Get user id
    user_profile = sp.me()
    user_id = user_profile['id']

    #Create Playlist
    sp.user_playlist_create(user=user_id, name=playlist_name, public=True)

    #Get lates playlist id
    playlist = sp.user_playlists(user=user_id)
    playlist_id = playlist['items'][0]['id']

    #Add recommendations track to playlist
    sp.playlist_add_items(playlist_id=playlist_id, items=recommendations_track_id)

# data = json.dumps(audio_features)
# print(data)

