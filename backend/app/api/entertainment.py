"""
A.B.E.L - Entertainment API Routes
Music, Movies, Anime, Games
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.services.entertainment.music_service import MusicService
from app.services.entertainment.movie_service import MovieService
from app.services.entertainment.anime_service import AnimeService
from app.services.entertainment.games_service import GamesService

router = APIRouter(prefix="/entertainment", tags=["Entertainment"])

# Service instances
music_service = MusicService()
movie_service = MovieService()
anime_service = AnimeService()
games_service = GamesService()


# ========================================
# MUSIC ENDPOINTS
# ========================================
@router.get("/music/search")
async def search_music(
    q: str = Query(..., description="Search query"),
    type: str = Query("track", description="Type: track, artist, album, playlist"),
    limit: int = Query(25, ge=1, le=100),
):
    """Search music on Deezer"""
    results = await music_service.deezer_search(q, type, limit)
    return {"results": results, "count": len(results)}


@router.get("/music/charts")
async def get_music_charts(limit: int = Query(50, ge=1, le=100)):
    """Get Deezer charts"""
    charts = await music_service.deezer_get_charts(limit)
    return {"charts": charts}


@router.get("/music/genres")
async def get_music_genres():
    """Get music genres"""
    genres = await music_service.deezer_get_genres()
    return {"genres": genres}


@router.get("/music/artist/{artist_id}")
async def get_artist(artist_id: int):
    """Get artist details from Deezer"""
    artist = await music_service.deezer_get_artist(artist_id)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist


@router.get("/music/album/{album_id}")
async def get_album(album_id: int):
    """Get album details from Deezer"""
    album = await music_service.deezer_get_album(album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Album not found")
    return album


@router.get("/music/lyrics")
async def get_lyrics(
    artist: str = Query(..., description="Artist name"),
    title: str = Query(..., description="Song title"),
):
    """Get song lyrics"""
    lyrics = await music_service.get_lyrics(artist, title)
    if not lyrics:
        raise HTTPException(status_code=404, detail="Lyrics not found")
    return {"artist": artist, "title": title, "lyrics": lyrics}


# ========================================
# MOVIES ENDPOINTS
# ========================================
@router.get("/movies/search")
async def search_movies(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
):
    """Search movies on TMDB"""
    results = await movie_service.search_movies(q, page)
    return {"results": results, "count": len(results)}


@router.get("/movies/popular")
async def get_popular_movies(page: int = Query(1, ge=1)):
    """Get popular movies"""
    movies = await movie_service.get_popular_movies(page)
    return {"movies": movies, "count": len(movies)}


@router.get("/movies/trending")
async def get_trending_movies(time_window: str = Query("week", regex="^(day|week)$")):
    """Get trending movies"""
    movies = await movie_service.get_trending_movies(time_window)
    return {"movies": movies, "count": len(movies)}


@router.get("/movies/upcoming")
async def get_upcoming_movies(page: int = Query(1, ge=1)):
    """Get upcoming movies"""
    movies = await movie_service.get_upcoming_movies(page)
    return {"movies": movies, "count": len(movies)}


@router.get("/movies/{movie_id}")
async def get_movie_details(movie_id: int):
    """Get movie details"""
    movie = await movie_service.get_movie_details(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/movies/{movie_id}/credits")
async def get_movie_credits(movie_id: int):
    """Get movie cast and crew"""
    credits = await movie_service.get_movie_credits(movie_id)
    return credits


# ========================================
# TV SHOWS ENDPOINTS
# ========================================
@router.get("/tv/search")
async def search_tv_shows(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
):
    """Search TV shows"""
    results = await movie_service.search_tv_shows(q, page)
    return {"results": results, "count": len(results)}


@router.get("/tv/popular")
async def get_popular_tv_shows(page: int = Query(1, ge=1)):
    """Get popular TV shows"""
    shows = await movie_service.get_popular_tv_shows(page)
    return {"shows": shows, "count": len(shows)}


@router.get("/tv/{tv_id}")
async def get_tv_show_details(tv_id: int):
    """Get TV show details"""
    show = await movie_service.get_tv_show_details(tv_id)
    if not show:
        raise HTTPException(status_code=404, detail="TV show not found")
    return show


# ========================================
# ANIME ENDPOINTS
# ========================================
@router.get("/anime/search")
async def search_anime(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=25),
):
    """Search anime on MyAnimeList (via Jikan)"""
    results = await anime_service.jikan_search(q, page, limit)
    return {"results": results, "count": len(results)}


@router.get("/anime/top")
async def get_top_anime(
    type: Optional[str] = Query(None, description="Type filter"),
    filter: Optional[str] = Query(None, description="airing, upcoming, bypopularity, favorite"),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=25),
):
    """Get top anime"""
    anime = await anime_service.jikan_top(type, filter, page, limit)
    return {"anime": anime, "count": len(anime)}


@router.get("/anime/seasonal")
async def get_seasonal_anime(
    year: Optional[int] = None,
    season: Optional[str] = Query(None, regex="^(winter|spring|summer|fall)$"),
):
    """Get seasonal anime"""
    anime = await anime_service.jikan_seasonal(year, season)
    return {"anime": anime, "count": len(anime)}


@router.get("/anime/{anime_id}")
async def get_anime_details(anime_id: int):
    """Get anime details from MyAnimeList"""
    anime = await anime_service.jikan_get_anime(anime_id)
    if not anime:
        raise HTTPException(status_code=404, detail="Anime not found")
    return anime


@router.get("/anime/anilist/search")
async def search_anime_anilist(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
):
    """Search anime on AniList"""
    results = await anime_service.anilist_search(q, page, per_page)
    return {"results": results, "count": len(results)}


@router.get("/anime/anilist/trending")
async def get_trending_anime_anilist(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=50),
):
    """Get trending anime from AniList"""
    anime = await anime_service.anilist_trending(page, per_page)
    return {"anime": anime, "count": len(anime)}


# ========================================
# GAMES ENDPOINTS
# ========================================
@router.get("/games/search")
async def search_games(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=40),
):
    """Search games on RAWG"""
    results = await games_service.rawg_search(q, page, page_size)
    return {"results": results, "count": len(results)}


@router.get("/games/popular")
async def get_popular_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=40),
):
    """Get popular games"""
    games = await games_service.rawg_popular(page, page_size)
    return {"games": games, "count": len(games)}


@router.get("/games/upcoming")
async def get_upcoming_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=40),
):
    """Get upcoming games"""
    games = await games_service.rawg_upcoming(page, page_size)
    return {"games": games, "count": len(games)}


@router.get("/games/{game_id}")
async def get_game_details(game_id: int):
    """Get game details"""
    game = await games_service.rawg_get_game(game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


@router.get("/games/deals")
async def get_game_deals(
    store_id: Optional[str] = None,
    page: int = Query(0, ge=0),
    page_size: int = Query(60, ge=1, le=60),
    sort_by: str = Query("Deal Rating", description="Sort criteria"),
):
    """Get game deals from CheapShark"""
    deals = await games_service.cheapshark_deals(store_id, page, page_size, sort_by)
    return {"deals": deals, "count": len(deals)}


@router.get("/games/free")
async def get_free_games(
    platform: Optional[str] = Query(None, description="pc, browser, all"),
    category: Optional[str] = Query(None, description="mmorpg, shooter, moba, etc."),
    sort_by: str = Query("relevance"),
):
    """Get free-to-play games"""
    games = await games_service.freetogame_list(platform, category, sort_by)
    return {"games": games, "count": len(games)}
