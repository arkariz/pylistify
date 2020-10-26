import os, sys
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render, redirect
from .models import getRecentTrack, getRecommendationsTrack, playlist

scope = 'user-library-read user-library-modify ' \
        'user-read-recently-played playlist-modify-private ' \
        'playlist-read-collaborative playlist-read-private playlist-modify-public'

cliend_id = '080e4d9856d645c396e08ec0b1088a02'
client_secret = '26b9fef0e6fc4b11a77618ba41e9cd20'
# Uri = 'http://127.0.0.1:8000/login/'
Uri = 'http://pylistify.herokuapp.com/login/'
username = sys.argv

sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope, username=username)

def index(request):
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Token Found")
        return render(request, 'index.html')
    else:
        print("Getting Token")
        auth_url = getSPOauthURI()
        htmlLoginButton = auth_url
        context = {
            'login': htmlLoginButton
        }
        return render(request, 'index.html', context)


def mainPage(request):
    token_info = sp_oauth.get_cached_token()
    if token_info:
        print("Access token available!")
        if request.method == 'POST':
            playlist_imput_name = request.POST.get('playlist')
            playlist(playlist_imput_name)
            os.remove('.cache')
            return render(request, 'success_notif.html')
        else:
            recentTrack = getRecentTrack()
            recommendationTrack = getRecommendationsTrack()

            context = {
                'artists': recentTrack['artist'],
                'tracks': recentTrack['track_name'],
                'songs' : recommendationTrack['songs']

            }

            return render(request, 'result.html', context)

def login(request):
    url = request.build_absolute_uri()
    code = sp_oauth.parse_response_code(url)
    print("Found Spotify auth code in Request URL! Trying to get valid access token...")
    token_info = sp_oauth.get_access_token(code)
    username = token_info['access_token']
    return redirect('/')

def getSPOauthURI():
    print("Getting Authorize url")
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
