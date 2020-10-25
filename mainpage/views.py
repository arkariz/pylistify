import sys
import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render
from .models import getRecentTrack, getRecommendationsTrack, playlist

scope = 'user-library-read user-library-modify user-read-recently-played playlist-modify-private playlist-read-collaborative playlist-read-private playlist-modify-public'

cliend_id = '080e4d9856d645c396e08ec0b1088a02'
client_secret = '26b9fef0e6fc4b11a77618ba41e9cd20'
Uri = 'https://elopakala.herokuapp.com/addplaylist/'

sp_oauth = oauth2.SpotifyOAuth(cliend_id, client_secret, Uri, scope=scope)

def index(request):
    access_token = ''
    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Token Found")
        access_token = token_info['access_token']
    else:
        url = request.build_absolute_uri()
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token:
        print("Access token available! Trying to get user information...")
        if request.method == 'POST':
            playlist_imput_name = request.POST.get('playlist')
            playlist(playlist_imput_name)
        else:
            recentTrack = getRecentTrack()
            recommendationTrack = getRecommendationsTrack()
            context = {
                'artists': recentTrack['artist'],
                'tracks': recentTrack['track_name'],
                'rartists': recommendationTrack['artist']
            }

            return render(request, 'result.html', context)

    else:
        # return htmlForLoginButton(request)
        if request.method == 'POST':
            playlist_imput_name = request.POST.get('playlist')
            playlist(playlist_imput_name)
        else:
            recentTrack = getRecentTrack()
            recommendationTrack = getRecommendationsTrack()
            context = {
                'artists': recentTrack['artist'],
                'tracks': recentTrack['track_name'],
                'rartists': recommendationTrack['artist']
            }

            return render(request, 'result.html', context)



def htmlForLoginButton(request):
    auth_url = getSPOauthURI()
    htmlLoginButton = auth_url
    context = {
        'login' : htmlLoginButton
    }
    return render(request, 'index.html', context )

def getSPOauthURI():
    auth_url = sp_oauth.get_authorize_url()
    return auth_url
