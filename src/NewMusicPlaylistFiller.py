import spotipy 
from spotipy.oauth2 import SpotifyOAuth

from src.data_structures import UserCredentials, SpotifyConfiguration, Playlist, Artist, Song
from typing import List, Set

import datetime
import time
from tqdm import tqdm

class NewMusicPlaylistFiller:
    def __init__(self, user_config: UserCredentials, spotify_config: SpotifyConfiguration, playlists: List[Playlist]):
        self.user_config = user_config
        self.spotify_config = spotify_config
        self.playlists = playlists

        self.spotify_client = self.create_spotify_client(self.user_config, self.spotify_config)

    @staticmethod
    def create_spotify_client(user_config: UserCredentials, spotify_config: SpotifyConfiguration):
        auth_manager=SpotifyOAuth(client_id = user_config.client_id,
                                client_secret = user_config.client_secret, 
                                redirect_uri = spotify_config.redirect_uri,
                                scope= spotify_config.scope)
        spotify_client = spotipy.Spotify(auth_manager= auth_manager, requests_timeout = 10)
        return spotify_client

    def get_all_artist_subscriptions(self, resultsLength = 50) -> Set[Artist]:
        subscribedArtists = set()
        lastBand = None
        while True:
            results = self.spotify_client.current_user_followed_artists(limit = resultsLength, after = lastBand)
            numArtists = len(results['artists']['items'])
            for idx, artist in enumerate(results['artists']['items']): subscribedArtists.add(Artist(artist['name'], artist['id']))
            time.sleep(self.spotify_config.rate_limit_interval)
            if idx == numArtists - 1: lastBand = artist['id']
            if numArtists < resultsLength: break
        return subscribedArtists

    def get_all_new_tracks(self, artists: Set[Artist]) -> Set[Song]:
        new_songs = set()
        for artist in tqdm(artists):
            new_tracks = self.get_artist_new_tracks(artist.id, self.spotify_config.time_span)
            new_songs |=new_tracks
        return new_songs

    def get_artist_new_tracks(self, artist_id: str, time_span: int = 28) -> Set[Song]:
        today = datetime.datetime.today()
        results = self.spotify_client.artist_albums(artist_id)
        album_tracks = set()
        for r in results["items"]:
            if (len(r["release_date"].split("-")) == 3) and (today - datetime.datetime(*[int(value) for value in r["release_date"].split("-")])).days < time_span:
                new_tracks = self.get_album_tracks(artist_id, r["id"])
                album_tracks |= new_tracks
        return album_tracks

    def get_album_tracks(self, artist_id: str, album_id: str) -> List[Song]:
        songs = set()
        results = self.spotify_client.album_tracks(album_id)
        for r in results["items"]:
            song_name = r["name"]
            song_id = r["id"]
            songs.add(Song(song_id, song_name, artist_id, None))
        return songs

    def fill_playlist(self, playlist: Playlist, songs: Set[Song], max_elements: int = 50):
        new_song_ids = [s.id for s in songs]
        self.clear_playlist(playlist.id)
        for i in range(0, len(new_song_ids), max_elements):
            self.spotify_client.playlist_add_items(playlist.id, new_song_ids[i:i+max_elements])
            time.sleep(0.5)

    def clear_playlist(self, playlist_id: str):
        self.spotify_client.playlist_replace_items(playlist_id, [])

    def run(self):
        artists = self.get_all_artist_subscriptions()
        songs = self.get_all_new_tracks(artists)
        self.fill_playlist(self.playlists[0], songs)