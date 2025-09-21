from dataclasses import dataclass, field
from typing import List, Set, FrozenSet

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
    genre: FrozenSet[str]

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
    songs: Set[Song] = field(default_factory=set)
    genres: Set[str] | None = None

    def __post_init__(self):
        self.genres = set() if (self.genres is None) else set(self.genres)
