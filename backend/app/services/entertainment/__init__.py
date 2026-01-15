"""
A.B.E.L - Entertainment Services
Music, Movies, TV, Games, Anime
"""

from app.services.entertainment.music_service import MusicService
from app.services.entertainment.movie_service import MovieService
from app.services.entertainment.anime_service import AnimeService
from app.services.entertainment.games_service import GamesService

__all__ = ["MusicService", "MovieService", "AnimeService", "GamesService"]
