from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .models import Playlist, Song
from .forms import PlaylistForm, SearchForm
from django.conf import settings
import requests
import pafy
import spotipy
import webbrowser
from spotipy.oauth2 import SpotifyClientCredentials
import random
import json
from django.views.decorators.csrf import csrf_exempt
from pytube import YouTube
from django.http import FileResponse, HttpResponse
from youtube_search import YoutubeSearch
import youtube_dl

@login_required
def index(request):
    playlists=request.user.playlists.all()
    form=PlaylistForm()
    search_form=SearchForm()
    sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    pl_url = sp_obj.category_playlists()['playlists']['items'][0]['href']
    number = random.randint(0, 40)
    name=sp_obj.playlist(pl_url)['tracks']['items'][number]['track']['album']['artists'][0]['name']
    album_name = sp_obj.playlist(pl_url)['tracks']['items'][number]['track']['album']['name']
    image = sp_obj.playlist(pl_url)['tracks']['items'][number]['track']['album']['images'][2]['url']
    username=request.user
    context={'playlists':playlists, 'form':form, 'search_form':search_form, 'name':name, 'image':image, 'album_name':album_name, 'username':username}
    return render(request, 'App/index.html', context)

def register(request):
    form=UserCreationForm()
    if request.method=="POST":
        form=UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data['username']
            password=form.cleaned_data['password1']
            user=authenticate(username=username, password=password)
            login(request, user)
            return redirect('../')
    context={'form':form}
    return render(request, 'registration/register.html', context)

def add(request):
    form=PlaylistForm()
    if request.method=="POST":
        form=PlaylistForm(request.POST)
        if form.is_valid():
            new_playlist=Playlist(text=request.POST['text'], user=request.user)
            new_playlist.save()
    return redirect('../')

def delete(request, playlist_id):
    playlist=request.user.playlists.get(pk=playlist_id)
    playlist.delete()
    return redirect('../../')

def playlist(request, playlist_id):
    search_form=SearchForm()
    playlist=request.user.playlists.get(pk=playlist_id)
    songs=playlist.songs.all()
    context={'songs':songs, 'playlist':playlist, 'search_form':search_form}
    return render(request, 'App/playlist.html',context)

def search(request):
    video_ids=[]
    video_titles=[]
    video_thumbnails=[]
    pictureFound=[]
    #search_url='https://www.googleapis.com/youtube/v3/search'
    #search_form=SearchForm()
    if request.method=="POST":
        search_form=SearchForm(request.POST)
        if search_form.is_valid():
            keyword=request.POST['keyword']
            # search_params={
            #     'part':'snippet',
            #     'key':settings.YOUTUBE_DATA_API_KEY,
            #     'q':keyword,
            #     'type':'video',
            #     'maxResults': 3
            # }
            # r=requests.get(search_url, params=search_params)
            # results=r.json()['items']
            # for result in results:
            #     video_ids.append((result['id']['videoId']).replace('&#39;',"'").replace('&amp;', '&'))
            #     video_titles.append(result['snippet']['title'].replace('&#39;',"'").replace('&amp;', '&'))
            #     video_thumbnails.append(result['snippet']['thumbnails']['default']['url'].replace('&#39;',"'").replace('&amp;', '&'))

            results = YoutubeSearch(keyword, max_results=3).to_dict()
            for i in range(len(results)):
                video_ids.append(results[i]['id'])
                video_titles.append(results[i]['title'])
                try:
                    video = pafy.new('https://www.youtube.com'+results[i]['link'])
                    video_thumbnails.append(video.thumb)
                    pictureFound.append(True)
                except:
                    video_thumbnails.append('https://image.flaticon.com/icons/png/512/181/181668.png')
                    pictureFound.append(False)
            videos=zip(video_ids,video_titles,video_thumbnails, pictureFound)
            #########################################################
            try:
                sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
                results = sp_obj.search(q='artist:' + keyword, type='artist')
                picture=results['artists']['items'][0]['images'][2]['url']
                name=results['artists']['items'][0]['name']
                artistFound=True
            except:
                picture=0
                name=0
                artistFound=False
            #########################################################
            try:
                sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
                results = sp_obj.search(q=keyword, type='album', limit=1)
                album_name=results['albums']['items'][0]['name']
                artist_name=results['albums']['items'][0]['artists'][0]['name']
                album_picture = results['albums']['items'][0]['images'][1]['url']
                albumFound=True
            except:
                album_name=''
                album_picture=''
                albumFound=False
            #########################################################
    context={'videos':videos, 'search_form':search_form,'found':artistFound,'picture':picture,'name':name, 'cover':album_picture,'album_name':album_name, 'albumFound':albumFound, 'artist_name':artist_name}
    return render(request, 'App/search.html', context)

def select(request, id, title):
    playlists=request.user.playlists.all()
    context={'playlists':playlists, 'id':id, 'title':title}
    return render(request, 'App/select.html', context)

def addtopl(request, playlist_id, id, title):
    playlistSelected=request.user.playlists.get(pk=playlist_id)
    song=Song(url=id, playlist=playlistSelected, title=title)
    song.save()
    return redirect('../../../../')

def removefrompl(request, playlist_id, song_id):
    playlistSelected=request.user.playlists.get(pk=playlist_id)
    songToDel=playlistSelected.songs.get(pk=song_id)
    songToDel.delete()
    return redirect('../../../playlist/'+str(playlist_id))

@csrf_exempt
def more(request,song_url,title):
    try:
        username = 'dgrqnco2rx8hdu58kv9if9eho'
        scope = 'user-read-private user-read-playback-state user-modify-playback-state'

        sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

        ss = title
        ss=ss.split('ft.')
        ss=ss[0]
        if ss.__contains__('('):
            q = ss[0:ss.index('(')]
        elif ss.__contains__('['):
            q = ss[0:ss.index('[')]
        elif ss.__contains__('{'):
            q = ss[0:ss.index('{')]
        else:
            q = ss
        query = sp_obj.search(q, 1, 0, 'track')

        # <<<<<<<<<<SONG>>>>>>>>>>

        # FIND THE SONG URI
        song_uri = query['tracks']['items'][0]['uri']

        track = sp_obj.track(song_uri)
        track_data = sp_obj.audio_features(song_uri)

        song_popularity = track['popularity']
        song_danceability = int(track_data[0]['danceability']*100)
        song_energy = track_data[0]['energy']
        song_loudness = track_data[0]['loudness']
        song_tempo = int(track_data[0]['tempo'])
        artist_uri = sp_obj.track(song_uri)['album']['artists'][0]['uri']
        artist = sp_obj.artist(artist_uri)['name']
        similar_artists = []
        pictures=[]
        endofrow=[]
        image=track['album']['images'][1]['url']
        for i in range(5):
            similar_artists.append(sp_obj.artist_related_artists(artist_uri)['artists'][i]['name'])
            pictures.append(sp_obj.artist_related_artists(artist_uri)['artists'][i]['images'][2]['url'])
            if i==1 or i==4:
                endofrow.append(True)
            else:
                endofrow.append(False)
        real_title=track['name']
        artists=zip(similar_artists,pictures,endofrow)
        isfound=True
    except:
        song_popularity="-"
        song_danceability ="-"
        song_tempo ="-"
        artist=''
        similar_artists=['','','','','']
        pictures=['','','','','']
        endofrow=['','','','','']
        artists = zip(similar_artists, pictures,endofrow)
        image=''
        real_title=title
        isfound=False


    if song_url=='1':
        results1 = YoutubeSearch(artist+" "+title, max_results=1).to_dict()
        song_url=results1[0]['id']
    search_form = SearchForm()
    url = 'http://www.youtube.com/watch?v=' + str(song_url)
    real_url=YouTube(url).streams.filter(only_audio=True).first().url
    ##################################################################################
    if image=='':
        image=YouTube(url).thumbnail_url
    ##################################################################################
    details = {'popularity': song_popularity, 'danceability': song_danceability, 'tempo': song_tempo, 'artist': artist,
               'artists': artists, 'image': image, 'isfound': isfound}
    context = {'url':song_url, 'song_title': real_title, 'details':details, 'search_form':search_form, 'real_url':real_url}
    return render(request, 'App/more.html', context)

def refresh(request):
    return redirect('../')

def album(request, album_name, artist_name):
    sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = sp_obj.search(q=album_name+" "+artist_name, type='album', limit=1)
    tracks = sp_obj.album_tracks(results['albums']['items'][0]['uri'])['items']
    names = []
    video_ids=[]
    similar_pictures=[]
    picture = results['albums']['items'][0]['images'][1]['url']
    for i in range(len(tracks)):
        names.append(tracks[i]['name'])
        video_ids.append('1')
    videos=zip(video_ids, names)
    search_form=SearchForm()
    ######################################################
    artist_uri = results['albums']['items'][0]['artists'][0]['uri']
    similar_artists = []
    similar_names=[]
    forbidden = []
    albums = []
    for i in range(3):
        index = random.randint(0, 4)
        while index in forbidden:
            index = random.randint(0, 4)
        similar_artists.append(sp_obj.artist_related_artists(artist_uri)['artists'][index]['uri'])
        similar_names.append(sp_obj.artist_related_artists(artist_uri)['artists'][index]['name'])
        forbidden.append(index)
    for i in similar_artists:
        index = random.randint(0, len(sp_obj.artist_albums(i)['items'])-1)
        albums.append(sp_obj.artist_albums(i)['items'][index]['name'])
        similar_pictures.append(sp_obj.artist_albums(i)['items'][index]['images'][1]['url'])
    #########################################################################
    context = {'album_name': album_name, 'picture': picture, 'videos': videos, 'name': artist_name, 'search_form': search_form, 'similar':zip(albums,similar_pictures,similar_names)}
    return render(request, 'App/album.html', context)

def artist(request,name):
    form=SearchForm()
    ################################
    sp_obj = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    results = sp_obj.search(q=name, type='artist', limit=1)
    genres_all = results['artists']['items'][0]['genres']
    genres = []
    if len(genres_all) >= 3:
        genres = genres_all[:3]
    else:
        genres = genres_all
    popularity = results['artists']['items'][0]['popularity']
    image = results['artists']['items'][0]['images'][0]['url']
    followers = results['artists']['items'][0]['followers']['total']
    uri = results['artists']['items'][0]['uri']
    albums_all = []
    pictures_all = []
    array = sp_obj.artist_albums(uri, album_type='album', limit=50)['items']
    for index in range(len(array)):
        albums_all.append(array[index]['name'])
        pictures_all.append(array[index]['images'][0]['url'])
    passedAlbums = []
    leng = len(albums_all)
    albums = []
    pictures = []
    for i in range(leng):
        if albums_all[i] not in passedAlbums:
            albums.append(albums_all[i])
            pictures.append(pictures_all[i])
        passedAlbums.append(albums_all[i])
    ################################
    similar_artists=[]
    artist_pictures=[]
    endofrow=[]
    for i in range(5):
        similar_artists.append(sp_obj.artist_related_artists(uri)['artists'][i]['name'])
        artist_pictures.append(sp_obj.artist_related_artists(uri)['artists'][i]['images'][2]['url'])
        if i == 0 or i==2 or i == 4:
            endofrow.append(True)
        else:
            endofrow.append(False)
    similar=zip(similar_artists,artist_pictures,endofrow)
    albpic=zip(albums,pictures)
    ################################
    context={'name':name, 'search_form':form,'genres':genres,'popularity':popularity, 'image':image, 'followers':followers, 'albpic':albpic, 'similar':similar}
    return render(request,'App/artist.html' ,context)
