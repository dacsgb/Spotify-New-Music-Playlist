import spotipy 
from spotipy.oauth2 import SpotifyOAuth

from src.data_structures import UserCredentials, Song, Album, Artist
from typing import List

import datetime
import time

class NewMusicPlaylistFiller:
    def __init__(self, user: UserCredentials, redirect_uri: str, app_scope: str, rate_limit_interval: int = 5):
        self.user = user
        self.rate_limit_interval = rate_limit_interval

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id= self.user.client_id,
                                                            client_secret= self.user.client_secret, 
                                                            redirect_uri = redirect_uri,
                                                            scope= app_scope),
                                    requests_timeout = 10)

    def get_all_artist_subscriptions(self) -> List[Artist]:
        subscribedArtists = []
        resultsLength = 50
        lastBand = None
        while True:
            results = self.sp.current_user_followed_artists(limit = resultsLength, after= lastBand)
            numArtists = len(results['artists']['items'])
            for idx, artist in enumerate(results['artists']['items']):
                if idx == numArtists - 1:
                    lastBand = artist['id']
                print(f"{idx + 1}/{numArtists} - {artist['name']}")
                albums = self.get_artist_new_albums(artist['id'])
                subscribedArtists.append(Artist(artist['name'], artist['id'], albums))
                time.sleep(self.rate_limit_interval)
            if numArtists < resultsLength:
                break
        return subscribedArtists

    def get_artist_new_albums(self, artist_id: str, time_span: int = 28) -> Album:
        today = datetime.datetime.today()
        artistNewAlbums= []
        resultsLength = 50
        lastAlbum = None
        results = self.sp.artist_albums(artist_id)
        for r in results["items"]:
            album_release_date = r["release_date"]
            if (len(album_release_date.split("-")) == 3) and (today - datetime.datetime(*[int(value) for value in r["release_date"].split("-")])).days < time_span:
                album_name = r["name"]
                album_id = r["id"]
                album_tracks = self.get_album_tracks(album_id)
                artistNewAlbums.append(Album(album_name, album_id, album_release_date, album_tracks))
        return artistNewAlbums

    def get_album_tracks(self, album_id: str) -> List[Song]:
        songs = []
        results = self.sp.album_tracks(album_id)
        for r in results["items"]:
            song_name = r["name"]
            song_id = r["id"]
            songs.append(Song(song_name, song_id))
        return songs

    def fill_new_music_playlist(self, artists: List[Artist], max_elements: int = 50):
        new_songs = []
        for a in artists: 
            if a.albums:
                for a in a.albums:
                    for s in a.tracks:
                        new_songs.append(s.id)
        self.clear_new_music_playlist()
        for i in range(0, len(new_songs), max_elements):
            self.sp.playlist_add_items(self.user.playlist_id, new_songs[i:i+max_elements])
            time.sleep(0.5)

    def clear_new_music_playlist(self):
        self.sp.playlist_replace_items(self.user.playlist_id, [])

    def run(self):
        subs = self.get_all_artist_subscriptions()
        self.fill_new_music_playlist(subs)