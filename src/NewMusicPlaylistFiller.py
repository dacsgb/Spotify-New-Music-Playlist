import spotipy 
from spotipy.oauth2 import SpotifyOAuth

from src.data_structures import UserCredentials, SpotifyConfiguration, Playlist, Artist, Song
from typing import List, Set, Tuple

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
        print("Creating Spotify Client")
        auth_manager=SpotifyOAuth(client_id = user_config.client_id,
                                    client_secret = user_config.client_secret, 
                                    redirect_uri = spotify_config.redirect_uri,
                                    scope= spotify_config.scope)
        spotify_client = spotipy.Spotify(auth_manager= auth_manager, requests_timeout = 10)
        print("Spotify Client Created\n")
        return spotify_client

    def get_all_artist_subscriptions(self, resultsLength = 50) -> Set[Artist]:
        print("Getting all artist subscriptions")
        subscribedArtists = set()
        lastBand = None
        i = 1
        total_artists = 0
        while True:
            results = self.spotify_client.current_user_followed_artists(limit = resultsLength, after = lastBand)
            numArtists = len(results['artists']['items'])
            total_artists += numArtists
            for idx, artist in enumerate(results['artists']['items']): subscribedArtists.add(Artist(artist['name'], artist['id']))
            print(f"\tIteration {i}: Retrieved {numArtists} more artists. Total: {total_artists}")
            i += 1
            time.sleep(self.spotify_config.rate_limit_interval)
            if idx == numArtists - 1: lastBand = artist['id']
            if numArtists < resultsLength: break
        print(f"\tTotal artist subscriptions: {total_artists}\n")
        return subscribedArtists

    def get_all_new_tracks(self, artists: Set[Artist]) -> Set[Song]:
        print("Getting all new songs")
        total_songs = 0
        new_songs = set()
        pbar = tqdm(artists, desc= f"Total songs = {total_songs}")
        for artist in pbar:
            new_tracks = self.get_artist_new_tracks(artist.id, self.spotify_config.time_span)
            new_songs |=new_tracks
            pbar.set_description(f"Total songs = {len(new_songs)}")
        print("\n")
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
        genres = frozenset(self.spotify_client.artist(artist_id)["genres"])
        for r in results["items"]:
            song_name = r["name"]
            song_id = r["id"]
            songs.add(Song(song_id, song_name, artist_id, genres))
        return songs

    def fill_playlists(self, playlists: List[Playlist]):
        print("Filling playlists")
        for playlist in playlists: self.fill_playlist(playlist)

    def fill_playlist(self, playlist: Playlist, max_elements: int = 50):
        print(f"\tFilling playlist {playlist.name} with {len(playlist.songs)} songs")
        new_song_ids = [s.id for s in playlist.songs]
        self.clear_playlist(playlist.id)
        for i in range(0, len(new_song_ids), max_elements):
            self.spotify_client.playlist_add_items(playlist.id, new_song_ids[i:i+max_elements])
            time.sleep(0.5)

    @staticmethod
    def genre_sorter(playlists: List[Playlist], songs: Set[Song]) -> Tuple[List[Playlist], Set[Song]] :
        print("Adding songs to relevant playlist")
        for song in songs:
            matching_score = [len(playlist.genres.intersection(song.genre)) for playlist in playlists]
            highest_matching = max(matching_score)
            if highest_matching == 0: continue
            matching_playlist = playlists[matching_score.index(highest_matching)]
            matching_playlist.songs.add(song)

        print("Finding outlying songs")
        for playlist in playlists: songs -= playlist.songs

        print("Filling outlier playlist")
        for playlist in playlists:
            if playlist.songs == set():
                playlist.songs = songs
                break

        print("Finished sorting by genre\n")
        return playlists

    def clear_playlist(self, playlist_id: str):
        self.spotify_client.playlist_replace_items(playlist_id, [])

    def run(self):
        artists = self.get_all_artist_subscriptions()
        songs = self.get_all_new_tracks(artists)
        playlists = self.genre_sorter(self.playlists, songs)
        self.fill_playlists(playlists)

