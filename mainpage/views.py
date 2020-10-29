import os, uuid
import spotipy
from spotipy import oauth2
from django.shortcuts import render, redirect

scope = 'user-library-read user-library-modify ' \
        'user-read-recently-played playlist-modify-private ' \
        'playlist-read-collaborative playlist-read-private playlist-modify-public'

cliend_id = '080e4d9856d645c396e08ec0b1088a02'
client_secret = '26b9fef0e6fc4b11a77618ba41e9cd20'
# Uri = 'http://127.0.0.1:8000/login/'
Uri = 'http://pylistify.herokuapp.com/login/'

cache_path = './.spotify_caches/'
if not os.path.exists(cache_path):
    os.makedirs(cache_path)


# ---------- Initiation ----------
def sessions_cache_path(request):
    return cache_path + request.session.get('uuid')

def index(request):
    if not request.session.get('uuid'):
        request.session['uuid'] = str(uuid.uuid4())

    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Token Found")
        recent_tracks = getRecentSong(request)
        context = {
            'recent_tracks': recent_tracks
        }
        return render(request, 'index.html', context)
    else:
        print("Getting Token")
        auth_url = sp_oauth.get_authorize_url()
        htmlLoginButton = auth_url
        context = {
            'login': htmlLoginButton
        }
        return render(request, 'index.html', context)

def login(request):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))

    url = request.build_absolute_uri()
    code = sp_oauth.parse_response_code(url)
    print("Found Spotify auth code in Request URL! Trying to get valid access token...")
    token_info = sp_oauth.get_access_token(code)
    return redirect('/')

def log_out(request):
    os.remove(sessions_cache_path(request))
    del request.session['uuid']

    return redirect('/')

# ---------- END Initiation


#---------- Get Recent Track Detail ----------
def getRecentTrack(request):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    if not sp_oauth.get_cached_token():
        return redirect('/')

    recent_track = sp.current_user_recently_played(limit=5)
    return recent_track

def getArtistId_recentTrack(request):
    recent_track = getRecentTrack(request)
    artist_id = []
    for idx, item in enumerate(recent_track['items']):
        track = item['track']
        artist = track['artists'][0]['id']
        artist_id.append(artist)
    return artist_id

def getTrackId_recentTrack(request):
    recent_track = getRecentTrack(request)
    track_id = []
    for idx, item in enumerate(recent_track['items']):
        track = item['track']
        track_feature = track['id']
        track_id.append(track_feature)
    return track_id

def getRecentSong(request):
    recent_track = getRecentTrack(request)
    tracks = []
    artists = []
    for idx, item in enumerate(recent_track['items']):
        track = item['track']
        tracks.append(track['name'])
        artists.append(track['artists'][0]['name'])

    content = [{'tracks': t[0], 'artists': t[1]} for t in zip(tracks, artists)]
    return content

def getRecentTrackAttribute(request):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    sp = spotipy.Spotify(auth_manager=sp_oauth)
    # Get track Attribute
    danceability = []
    energy = []
    tempo = []
    loudness = []
    for item_id in getTrackId_recentTrack(request):
        audio_features = sp.audio_features(tracks=item_id)
        for idx, item in enumerate(audio_features):
            danceability.append(item['danceability'])
            energy.append(item['energy'])
            tempo.append(item['tempo'])
            loudness.append(item['loudness'])
    content = {
        'danceability':danceability,
        'energy':energy,
        'tempo':tempo,
        'loudness':loudness,
    }
    return content

#---------- END Get Recent Track Detail ----------


# --------- Get Recommendation Track ----------
def getRecommendationsTrack(request):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    if not sp_oauth.get_cached_token():
        return redirect('/')

    attribute = getRecentTrackAttribute(request)
    danceability = attribute.get('danceability')
    energy = attribute.get('energy')
    tempo = attribute.get('tempo')
    loudness = attribute.get('loudness')


    recommendations_track_id = []
    tracks = []
    artists = []
    recommendations = sp.recommendations(seed_artists=getArtistId_recentTrack(request), min_danceability=min(danceability),
                                         max_danceability=max(danceability), min_tempo=min(tempo),
                                         max_tempo=max(tempo), min_energy=min(energy), max_energy=max(energy),
                                         min_loudness=min(loudness))

    for idx, item in enumerate(recommendations['tracks']):
        # print(idx, item['artists'][0]['name'], " – ", item['name'])
        tracks.append(item['name'])
        artists.append(item['artists'][0]['name'])
        track_id = item['id']
        recommendations_track_id.append(track_id)

    songs = [{'tracks': t[0], 'artists': t[1]} for t in zip(tracks, artists)]
    content = {
        'r_track_id': recommendations_track_id,
        'songs' : songs
    }
    return content

# --------- END Get Recommendation Track ----------


# --------- PLAYLIST ----------
def playlist(request, playlist_name):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    sp = spotipy.Spotify(auth_manager=sp_oauth)

    if not sp_oauth.get_cached_token():
        return redirect('/')

    # Get user id
    user_profile = sp.me()
    user_id = user_profile['id']

    #Create Playlist
    sp.user_playlist_create(user=user_id, name=playlist_name, public=True)

    #Get lates playlist id
    playlist = sp.user_playlists(user=user_id)
    playlist_id = playlist['items'][0]['id']

    #Add recommendations track to playlist
    r_track_id = getRecommendationsTrack(request)
    recommendations_track_id = r_track_id.get('r_track_id')
    sp.playlist_add_items(playlist_id=playlist_id, items=recommendations_track_id)

# --------- END PLAYLIST ----------


def mainPage(request):
    sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, cache_path=sessions_cache_path(request))
    token_info = sp_oauth.get_cached_token()

    if not sp_oauth.get_cached_token():
        return redirect('/')

    if token_info:
        print("Access token available!")
        if request.method == 'POST':
            playlist_imput_name = request.POST.get('playlist')
            playlist(request, playlist_imput_name)
            return render(request, 'success_notif.html')
        else:

            recommendationTrack = getRecommendationsTrack(request)

            context = {
                'songs' : recommendationTrack['songs']
            }

            return render(request, 'result.html', context)
    else:
        return redirect('/')