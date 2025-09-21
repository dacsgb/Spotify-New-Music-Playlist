import yaml

from src.data_structures import UserCredentials, SpotifyConfiguration, Playlist
from src.NewMusicPlaylistFiller import NewMusicPlaylistFiller

from typing import List, Dict

def load_yaml(file_path: str):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def parse_user_config(data: Dict[str, str]) -> UserCredentials:
    user_config = UserCredentials(**data)
    return user_config

def parse_spotify_config(data: Dict[str, str]) -> SpotifyConfiguration:
    spotify_config = SpotifyConfiguration(**data)
    return spotify_config

def parse_playlist_config(data: Dict[str, Dict[str, str|List[str]]]) -> List[Playlist]:
    playlists = [Playlist(name = playlist_name, **playlist_data) for playlist_name, playlist_data in data.items()]
    return playlists

def main():

    user = parse_user_config(load_yaml('config/user_config.yaml'))
    spotify = parse_spotify_config(load_yaml("config/app_config.yaml"))
    playlists= parse_playlist_config(load_yaml("config/playlist_config.yaml"))

    app = NewMusicPlaylistFiller(user_config = user,
                                spotify_config = spotify,
                                playlists = playlists)
    
    app.run()

if __name__ == "__main__":
    main()