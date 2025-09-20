from dataclasses import dataclass
from typing import List

@dataclass(frozen= True)
class UserCredentials:
    client_id: str
    client_secret: str
    playlist_id: str

@dataclass
class Song:
    name: str
    id: str

@dataclass
class Album:
    name: str
    id: str
    release_date: str
    tracks: List[Song]

@dataclass
class Artist:
    name: str
    id: str
    albums: List[Album] | None
