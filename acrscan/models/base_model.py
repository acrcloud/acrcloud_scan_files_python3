#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Do not change this file

from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, Callable, cast, Union
from datetime import datetime
import dateutil.parser

T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def is_type(t: Type[T], x: Any) -> T:
    assert isinstance(x, t)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


@dataclass
class Status:
    def __init__(self, msg, code, version):
        self.msg = msg
        self.code = code
        self.version = version

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        msg = from_union([from_str, from_none], obj.get("msg"))
        code = from_union([from_int, from_none], obj.get("code"))
        version = from_union([from_str, from_none], obj.get("version"))
        return Status(msg, code, version)

    def to_dict(self):
        result = {"msg": from_union([from_str, from_none], self.msg),
                  "code": from_union([from_int, from_none], self.code),
                  "version": from_union([from_str, from_none], self.version)}
        return result


@dataclass
class Response:
    def __init__(self, status, metadata, cost_time, result_type):
        self.status = status
        self.metadata = metadata
        self.cost_time = cost_time
        self.result_type = result_type

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        status = from_union([Status.from_dict, from_none], obj.get("status"))
        metadata = from_union([Metadata.from_dict, from_none], obj.get("metadata"))
        cost_time = from_union([from_float, from_none], obj.get("cost_time"))
        result_type = from_union([from_int, from_none], obj.get("result_type"))
        return Response(status, metadata, cost_time, result_type)

    def to_dict(self):
        result = {"status": from_union([lambda x: to_class(Status, x), from_none], self.status),
                  "metadata": from_union([lambda x: to_class(Metadata, x), from_none], self.metadata),
                  "cost_time": from_union([to_float, from_none], self.cost_time),
                  "result_type": from_union([from_int, from_none], self.result_type)}
        return result


@dataclass
class Metadata:
    def __init__(self, timestamp_utc, custom_files, music):
        self.timestamp_utc = timestamp_utc
        self.custom_files = custom_files
        self.music = music

    @staticmethod
    def from_dict(obj):
        assert isinstance(obj, dict)
        timestamp_utc = from_union([from_datetime, from_none], obj.get("timestamp_utc"))
        custom_files = from_union([lambda x: from_list(CustomFile.from_dict, x), from_none], obj.get("custom_files"))
        music = from_union([lambda x: from_list(Music.from_dict, x), from_none], obj.get("music"))
        return Metadata(timestamp_utc, custom_files, music)

    def to_dict(self):
        result = {"timestamp_utc": from_union([lambda x: x.isoformat(), from_none], self.timestamp_utc),
                  "custom_files": from_union([lambda x: from_list(lambda x: to_class(CustomFile, x), x), from_none],
                                             self.custom_files),
                  "music": from_union([lambda x: from_list(lambda x: to_class(Music, x), x), from_none], self.music)}
        return result


@dataclass
class GenreClass:
    name: Optional[str] = None
    id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'GenreClass':
        assert isinstance(obj, dict)
        name = from_union([from_str, from_none], obj.get("name"))
        return GenreClass(name)

    def to_dict(self) -> dict:
        result: dict = {"name": from_union([from_str, from_none], self.name),
                        }
        return result


@dataclass
class GenresNullClass:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'GenresNullClass':
        assert isinstance(obj, dict)
        return GenresNullClass()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class ExternalIDS:
    isrc: Optional[str] = None
    upc: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ExternalIDS':
        assert isinstance(obj, dict)
        isrc = from_union([from_str, from_none], obj.get("isrc"))
        upc = from_union([from_str, from_none], obj.get("upc"))
        return ExternalIDS(isrc, upc)

    def to_dict(self) -> dict:
        result: dict = {"isrc": from_union([from_str, from_none], self.isrc),
                        "upc": from_union([from_str, from_none], self.upc)}
        return result


@dataclass
class DeezerAlbum:
    id: Optional[int] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'DeezerAlbum':
        assert isinstance(obj, dict)
        id = from_union([from_int, from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))

        return DeezerAlbum(id, name)

    def to_dict(self) -> dict:
        result: dict = {"id": from_union([from_int, from_str, from_none], self.id),
                        "name": from_union([from_str, from_none], self.name)}
        return result


@dataclass
class Deezer:
    genres: Union[List[DeezerAlbum], GenresNullClass, None]

    album: Optional[DeezerAlbum] = None
    artists: Optional[List[DeezerAlbum]] = None
    track: Optional[DeezerAlbum] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Deezer':
        assert isinstance(obj, dict)
        genres = from_union([lambda x: from_list(DeezerAlbum.from_dict, x), GenresNullClass.from_dict, from_none],
                            obj.get("genres"))
        track = from_union([DeezerAlbum.from_dict, from_none], obj.get("track"))
        artists = from_union([lambda x: from_list(DeezerAlbum.from_dict, x), from_none], obj.get("artists"))
        album = from_union([DeezerAlbum.from_dict, from_none], obj.get("album"))
        return Deezer(genres, track, artists, album)

    def to_dict(self) -> dict:
        result: dict = {"genres": from_union(
            [lambda x: from_list(lambda x: to_class(DeezerAlbum, x), x), lambda x: to_class(GenresNullClass, x),
             from_none], self.genres), "track": from_union([lambda x: to_class(DeezerAlbum, x), from_none], self.track),
            "artists": from_union([lambda x: from_list(lambda x: to_class(DeezerAlbum, x), x), from_none],
                                  self.artists),
            "album": from_union([lambda x: to_class(DeezerAlbum, x), from_none], self.album)}
        return result


@dataclass
class SpotifyAlbum:
    id: Optional[str] = None
    name: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'SpotifyAlbum':
        assert isinstance(obj, dict)
        id = from_union([from_str, from_none], obj.get("id"))
        name = from_union([from_str, from_none], obj.get("name"))

        return SpotifyAlbum(id, name)

    def to_dict(self) -> dict:
        result: dict = {"id": from_union([from_str, from_none], self.id),
                        "name": from_union([from_str, from_none], self.name)}

        return result


@dataclass
class Spotify:
    album: Optional[SpotifyAlbum] = None
    artists: Optional[List[SpotifyAlbum]] = None
    track: Optional[SpotifyAlbum] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Spotify':
        assert isinstance(obj, dict)
        album = from_union([SpotifyAlbum.from_dict, from_none], obj.get("album"))
        artists = from_union([lambda x: from_list(SpotifyAlbum.from_dict, x), from_none], obj.get("artists"))
        track = from_union([SpotifyAlbum.from_dict, from_none], obj.get("track"))
        return Spotify(album, artists, track)

    def to_dict(self) -> dict:
        result: dict = {"album": from_union([lambda x: to_class(SpotifyAlbum, x), from_none], self.album),
                        "artists": from_union([lambda x: from_list(lambda x: to_class(SpotifyAlbum, x), x), from_none],
                                              self.artists),
                        "track": from_union([lambda x: to_class(SpotifyAlbum, x), from_none], self.track)}
        return result


@dataclass
class Youtube:
    vid: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Youtube':
        assert isinstance(obj, dict)
        vid = from_union([from_str, from_none], obj.get("vid"))
        return Youtube(vid)

    def to_dict(self) -> dict:
        result: dict = {"vid": from_union([from_str, from_none], self.vid)}
        return result


@dataclass
class ExternalMetadata:
    youtube: Optional[Youtube] = None
    spotify: Optional[Spotify] = None
    deezer: Optional[Deezer] = None

    @staticmethod
    def from_dict(obj: Any) -> 'ExternalMetadata':
        assert isinstance(obj, dict)
        youtube = from_union([Youtube.from_dict, from_none], obj.get("youtube"))
        spotify = from_union([Spotify.from_dict, from_none], obj.get("spotify"))
        deezer = from_union([Deezer.from_dict, from_none], obj.get("deezer"))
        return ExternalMetadata(youtube, spotify, deezer)

    def to_dict(self) -> dict:
        result: dict = {"youtube": from_union([lambda x: to_class(Youtube, x), from_none], self.youtube),
                        "spotify": from_union([lambda x: to_class(Spotify, x), from_none], self.spotify),
                        "deezer": from_union([lambda x: to_class(Deezer, x), from_none], self.deezer)}
        return result


@dataclass
class Music:
    external_ids: Optional[ExternalIDS] = None
    sample_begin_time_offset_ms: Optional[int] = None
    sample_end_time_offset_ms: Optional[int] = None
    label: Optional[str] = None
    duration_ms: Optional[int] = None
    acrid: Optional[str] = None
    db_begin_time_offset_ms: Optional[int] = None
    play_offset_ms: Optional[int] = None
    release_date: Optional[str] = None
    genres: Optional[List[GenreClass]] = None
    score: Optional[int] = None
    title: Optional[str] = None
    external_metadata: Optional[ExternalMetadata] = None
    album: Optional[GenreClass] = None
    db_end_time_offset_ms: Optional[int] = None
    result_from: Optional[int] = None
    artists: Optional[List[GenreClass]] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Music':
        assert isinstance(obj, dict)
        external_ids = from_union([ExternalIDS.from_dict, from_none], obj.get("external_ids"))
        sample_begin_time_offset_ms = from_union([from_int, from_none], obj.get("sample_begin_time_offset_ms"))
        sample_end_time_offset_ms = from_union([from_int, from_none], obj.get("sample_end_time_offset_ms"))
        label = from_union([from_str, from_none], obj.get("label"))
        duration_ms = from_union([from_int, from_none], obj.get("duration_ms"))
        acrid = from_union([from_str, from_none], obj.get("acrid"))
        db_begin_time_offset_ms = from_union([from_int, from_none], obj.get("db_begin_time_offset_ms"))
        play_offset_ms = from_union([from_int, from_none], obj.get("play_offset_ms"))
        release_date = from_union([from_str, from_none], obj.get("release_date"))
        genres = from_union([lambda x: from_list(GenreClass.from_dict, x), from_none], obj.get("genres"))
        score = from_union([from_int, from_none], obj.get("score"))
        title = from_union([from_str, from_none], obj.get("title"))
        external_metadata = from_union([ExternalMetadata.from_dict, from_none], obj.get("external_metadata"))
        album = from_union([GenreClass.from_dict, from_none], obj.get("album"))
        db_end_time_offset_ms = from_union([from_int, from_none], obj.get("db_end_time_offset_ms"))
        result_from = from_union([from_int, from_none], obj.get("result_from"))
        artists = from_union([lambda x: from_list(GenreClass.from_dict, x), from_none], obj.get("artists"))

        return Music(external_ids, sample_begin_time_offset_ms, sample_end_time_offset_ms, label, duration_ms, acrid,
                     db_begin_time_offset_ms, play_offset_ms, release_date, genres, score, title, external_metadata,
                     album, db_end_time_offset_ms, result_from, artists)

    def to_dict(self) -> dict:
        result: dict = {"external_ids": from_union([lambda x: to_class(ExternalIDS, x), from_none], self.external_ids),
                        "sample_begin_time_offset_ms": from_union([from_int, from_none],
                                                                  self.sample_begin_time_offset_ms),
                        "sample_end_time_offset_ms": from_union([from_int, from_none], self.sample_end_time_offset_ms),
                        "label": from_union([from_str, from_none], self.label),
                        "duration_ms": from_union([from_int, from_none], self.duration_ms),
                        "acrid": from_union([from_str, from_none], self.acrid),
                        "db_begin_time_offset_ms": from_union([from_int, from_none], self.db_begin_time_offset_ms),
                        "play_offset_ms": from_union([from_int, from_none], self.play_offset_ms),
                        "release_date": from_union([from_str, from_none], self.release_date),
                        "genres": from_union([lambda x: from_list(lambda x: to_class(GenreClass, x), x), from_none],
                                             self.genres), "score": from_union([from_int, from_none], self.score),
                        "title": from_union([from_str, from_none], self.title),
                        "external_metadata": from_union([lambda x: to_class(ExternalMetadata, x), from_none],
                                                        self.external_metadata),
                        "album": from_union([lambda x: to_class(GenreClass, x), from_none], self.album),
                        "db_end_time_offset_ms": from_union([from_int, from_none], self.db_end_time_offset_ms),
                        "result_from": from_union([from_int, from_none], self.result_from),
                        "artists": from_union([lambda x: from_list(lambda x: to_class(GenreClass, x), x), from_none],
                                              self.artists)}
        return result


@dataclass
class CustomFile:
    audio_id: Optional[int] = None
    bucket_id: Optional[int] = None
    duration_ms: Optional[int] = None
    sample_begin_time_offset_ms: Optional[int] = None
    sample_end_time_offset_ms: Optional[int] = None
    title: Optional[str] = None
    db_end_time_offset_ms: Optional[int] = None
    db_begin_time_offset_ms: Optional[int] = None
    acrid: Optional[str] = None
    play_offset_ms: Optional[int] = None
    score: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'CustomFile':
        assert isinstance(obj, dict)
        audio_id = from_union([from_none, lambda x: int(from_str(x))], obj.get("audio_id"))
        bucket_id = from_union([from_none, lambda x: int(from_str(x))], obj.get("bucket_id"))
        duration_ms = from_union([from_none, lambda x: int(from_str(x))], obj.get("duration_ms"))
        sample_begin_time_offset_ms = from_union([from_int, from_none], obj.get("sample_begin_time_offset_ms"))
        sample_end_time_offset_ms = from_union([from_int, from_none], obj.get("sample_end_time_offset_ms"))
        title = from_union([from_str, from_none], obj.get("title"))
        db_end_time_offset_ms = from_union([from_int, from_none], obj.get("db_end_time_offset_ms"))
        db_begin_time_offset_ms = from_union([from_int, from_none], obj.get("db_begin_time_offset_ms"))
        acrid = from_union([from_str, from_none], obj.get("acrid"))
        play_offset_ms = from_union([from_int, from_none], obj.get("play_offset_ms"))
        score = from_union([from_int, ], obj.get("score"))

        return CustomFile(audio_id, bucket_id, duration_ms, sample_begin_time_offset_ms,
                          sample_end_time_offset_ms, title, db_end_time_offset_ms, db_begin_time_offset_ms, acrid,
                          play_offset_ms, score)

    def to_dict(self) -> dict:
        result: dict = {"audio_id": from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                                lambda x: from_str((lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                               self.audio_id),
                        "bucket_id": from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                                 lambda x: from_str(
                                                     (lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                                self.bucket_id),
                        "duration_ms": from_union([lambda x: from_none((lambda x: is_type(type(None), x))(x)),
                                                   lambda x: from_str(
                                                       (lambda x: str((lambda x: is_type(int, x))(x)))(x))],
                                                  self.duration_ms),
                        "sample_begin_time_offset_ms": from_union([from_int, from_none],
                                                                  self.sample_begin_time_offset_ms),
                        "sample_end_time_offset_ms": from_union([from_int, from_none], self.sample_end_time_offset_ms),
                        "title": from_union([from_str, from_none], self.title),
                        "db_end_time_offset_ms": from_union([from_int, from_none], self.db_end_time_offset_ms),
                        "db_begin_time_offset_ms": from_union([from_int, from_none], self.db_begin_time_offset_ms),
                        "acrid": from_union([from_str, from_none], self.acrid),
                        "play_offset_ms": from_union([from_int, from_none], self.play_offset_ms),
                        "score": from_union([from_int, from_none], self.score)
                        }
        return result


@dataclass
class BaseResult:
    filename: Optional[str] = None
    status_code: Optional[int] = None
    start_time_ms: Optional[int] = None
    end_time_ms: Optional[int] = None
    duration_ms: Optional[int] = None
    played_duration_ms: Optional[int] = None
    title: Optional[str] = None
    score: Optional[int] = None
    acrid: Optional[str] = None
    sample_begin_time_offset_ms: Optional[int] = None
    sample_end_time_offset_ms: Optional[int] = None
    db_begin_time_offset_ms: Optional[int] = None
    db_end_time_offset_ms: Optional[int] = None


class MusicResult(BaseResult):
    similar_results: Optional[List[Music]] = None
    artists_names: Optional[str] = None
    isrc: Optional[str] = None
    upc: Optional[str] = None
    spotify_id: Optional[str] = None
    youtube_id: Optional[str] = None
    deezer_id: Optional[str] = None
    release_date: Optional[str] = None
    label: Optional[str] = None
    primary_result: Optional[Music] = None

    def to_dict(self) -> dict:
        result: dict = {"filename": from_union([from_str, from_none], self.filename),
                        "status_code": from_union([from_int, from_none], self.status_code),
                        "start_time_ms": from_union([from_str, from_int, from_none], self.start_time_ms),
                        "end_time_ms": from_union([from_str, from_int, from_none], self.end_time_ms),
                        "duration_ms": from_union([from_int, from_none], self.duration_ms),
                        "played_duration_ms": from_union([from_int, from_none], self.played_duration_ms),
                        "title": from_union([from_str, from_none], self.title),
                        "score": from_union([from_int, from_none], self.score),
                        "similar_results": from_union([lambda x: from_list(lambda x: to_class(Music, x), x), from_none],
                                                      self.similar_results),
                        "artists_names": from_union([from_str, from_none], self.artists_names),
                        "isrc": from_union([from_str, from_none], self.isrc),
                        "upc": from_union([from_str, from_none], self.upc),
                        "spotify_id": from_union([from_str, from_none], self.spotify_id),
                        "youtube_id": from_union([from_str, from_none], self.youtube_id),
                        "deezer_id": from_union([from_str, from_int, from_none], self.deezer_id),
                        "release_date": from_union([from_str, from_none], self.release_date),
                        "label": from_union([from_str, from_none], self.label),
                        "acrid": from_union([from_str, from_none], self.acrid),

                        "sample_begin_time_offset_ms": from_union([from_int, from_none],
                                                                  self.sample_begin_time_offset_ms),
                        "sample_end_time_offset_ms": from_union([from_int, from_none],
                                                                self.sample_end_time_offset_ms),
                        "db_begin_time_offset_ms": from_union([from_int, from_none],
                                                              self.db_begin_time_offset_ms),
                        "db_end_time_offset_ms": from_union([from_int, from_none],
                                                            self.db_end_time_offset_ms),
                        }
        return result


class CustomFileResult(BaseResult):
    similar_results: Optional[List[CustomFile]] = None
    audio_id: Optional[int] = None
    bucket_id: Optional[int] = None
    acrid: Optional[str] = None
    primary_result: Optional[CustomFile] = None

    def to_dict(self) -> dict:
        result: dict = {"filename": from_union([from_str, from_none], self.filename),
                        "status_code": from_union([from_int, from_none], self.status_code),
                        "start_time_ms": from_union([from_str, from_int, from_none], self.start_time_ms),
                        "end_time_ms": from_union([from_str, from_int, from_none], self.end_time_ms),
                        "duration_ms": from_union([from_int, from_none], self.duration_ms),
                        "played_duration_ms": from_union([from_int, from_none], self.played_duration_ms),
                        "title": from_union([from_str, from_none], self.title),
                        "score": from_union([from_int, from_none], self.score),
                        "similar_results": from_union(
                            [lambda x: from_list(lambda x: to_class(CustomFile, x), x), from_none],
                            self.similar_results),
                        "audio_id": from_union([from_int, from_str, from_none], self.audio_id),
                        "bucket_id": from_union([from_int, from_str, from_none], self.bucket_id),
                        "acrid": from_union([from_str, from_none], self.acrid),
                        "sample_begin_time_offset_ms": from_union([from_int, from_none],
                                                                  self.sample_begin_time_offset_ms),
                        "sample_end_time_offset_ms": from_union([from_int, from_none],
                                                                self.sample_end_time_offset_ms),
                        "db_begin_time_offset_ms": from_union([from_int, from_none],
                                                              self.db_begin_time_offset_ms),
                        "db_end_time_offset_ms": from_union([from_int, from_none],
                                                            self.db_end_time_offset_ms),
                        }
        return result


def response_from_dict(s: Any) -> Response:
    return Response.from_dict(s)


def response_to_dict(x: Response) -> Any:
    return to_class(Response, x)
