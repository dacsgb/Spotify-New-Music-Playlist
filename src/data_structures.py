from dataclasses import dataclass
from typing import List

@dataclass(frozen= True)
class UserCredentials:
    client_id: str
    client_secret: str

@dataclass(frozen= True)
class SpotifyConfiguration:
    redirect_uri: str
    scope: str
    time_span: int
    rate_limit_interval: int

@dataclass(frozen = True)
class Song:
    id: str
    name: str
    artist: str
    genre: str

    def __eq__(self, value):
        eq = True
        eq &= (self.name == value.name)
        eq &= (self.artist == value.artist)
        return eq

@dataclass(frozen = True)
class Artist:
    name: str
    id: str

@dataclass
class Album:
    name: str
    id: str
    release_date: str
    tracks: List[Song]

@dataclass
class Playlist:
    name: str
    id: str
    genres: List[str]
    songs: Song | None = None