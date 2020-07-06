#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# Do not change this file


class Status:
    def __init__(self, msg, code, version):
        self.msg = msg
        self.code = code
        self.version = version

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        msg = obj.get("msg")
        code = obj.get("code")
        version = obj.get("version")
        return Status(msg, code, version)

    def to_dict(self):
        result = {"msg": self.msg,
                  "code": self.code,
                  "version": self.version}
        return result


class Response:
    def __init__(self, status=None, metadata=None, cost_time=None, result_type=None):
        self.status = status
        self.metadata = metadata
        self.cost_time = cost_time
        self.result_type = result_type

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            status = Status.from_dict(obj.get("status"))
            metadata = Metadata.from_dict(obj.get("metadata"))
            cost_time = obj.get("cost_time")
            result_type = obj.get("result_type")
            return Response(status, metadata, cost_time, result_type)
        else:
            return Response()

    def to_dict(self):
        result = {"status": self.status.to_dict() if self.status else None,
                  "metadata": self.metadata.to_dict() if self.metadata else None,
                  "cost_time": self.cost_time,
                  "result_type": self.result_type
                  }
        return result


class Metadata:
    def __init__(self, timestamp_utc=None, custom_files=None, music=None):
        self.timestamp_utc = timestamp_utc
        self.custom_files = custom_files
        self.music = music

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            timestamp_utc = obj.get("timestamp_utc")
            custom_files = obj.get("custom_files")
            music = obj.get("music")

            return Metadata(timestamp_utc,
                            [CustomFile.from_dict(c) for c in custom_files] if custom_files else None,
                            [Music.from_dict(m) for m in music] if music else None
                            )
        else:
            return Metadata()

    def to_dict(self):
        result = {"timestamp_utc": self.timestamp_utc,
                  "custom_files": [c.to_dict() for c in self.custom_files] if self.custom_files else None,
                  "music": [m.to_dict() for m in self.music] if self.music else None}
        return result


class ExternalIDS:
    def __init__(self, isrc=None, upc=None):
        self.isrc = isrc
        self.upc = upc

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            isrc = obj.get("isrc")
            upc = obj.get("upc")
            return ExternalIDS(isrc, upc)
        else:
            return ExternalIDS()

    def to_dict(self) -> dict:
        result = {"isrc": self.isrc,
                  "upc": self.upc}
        return result


class Item:
    def __init__(self, id=None, name=None, ):
        self.id = id
        self.name = name

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            id = obj.get("id")

            name = obj.get("name")
            return Item(id, name)
        else:
            return Item()

    def to_dict(self):
        result = {"id": self.id,
                  "name": self.name
                  }
        return result


class Deezer:
    def __init__(self, genres=None, album=Item(), artists=None, track=Item()):
        if genres is None:
            genres = [Item()]
        if artists is None:
            artists = [Item()]
        self.genres = genres
        self.album = album
        self.artists = artists
        self.track = track

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            genres = obj.get("genres")
            track = obj.get("track")
            artists = obj.get("artists")
            album = obj.get("album")
            return Deezer(genres=[Item.from_dict(g) for g in genres] if genres else [Item()],
                          album=Item.from_dict(track),
                          artists=[Item.from_dict(a) for a in artists] if artists else [Item()],
                          track=Item.from_dict(album)
                          )
        else:
            return Deezer()

    def to_dict(self):
        result = {"genres": [g.to_dict() for g in self.genres],
                  "track": self.track.to_dict(),
                  "artists": [a.to_dict() for a in self.artists],
                  "album": self.album.to_dict()
                  }
        return result


class Spotify:
    def __init__(self, album=Item(), artists=None, track=Item()):
        if artists is None:
            artists = [Item()]
        self.album = album
        self.artists = artists
        self.track = track

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            album = obj.get("album")
            artists = obj.get("artists")
            track = obj.get("track")

            return Spotify(Item.from_dict(album) if album else Item(),
                           [Item.from_dict(a) for a in artists] if artists else [Item()],
                           Item.from_dict(track) if track else Item()
                           )
        else:
            return Spotify()

    def to_dict(self):
        result = {"album": self.album.to_dict(),
                  "artists": [a.to_dict() for a in self.artists],
                  "track": self.track.to_dict()
                  }
        return result


class Youtube:
    def __init__(self, vid=None):
        self.vid = vid

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            vid = obj.get("vid")
            return Youtube(vid)
        else:
            return Youtube()

    def to_dict(self):
        result = {"vid": self.vid}
        return result


class ExternalMetadata:
    def __init__(self, youtube=None, spotify=None, deezer=None):
        self.youtube = youtube
        self.spotify = spotify
        self.deezer = deezer

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            youtube = Youtube.from_dict(obj.get("youtube"))
            spotify = Spotify.from_dict(obj.get("spotify"))
            deezer = Deezer.from_dict(obj.get("deezer"))
            return ExternalMetadata(youtube, spotify, deezer)
        else:
            return ExternalMetadata()

    def to_dict(self):
        result = {"youtube": self.youtube.to_dict() if self.youtube else None,
                  "spotify": self.spotify.to_dict() if self.spotify else None,
                  "deezer": self.deezer.to_dict() if self.deezer else None
                  }
        return result


class Contributors:
    def __init__(self, composers=None, lyricists=None):
        self.composers = composers
        self.lyricists = lyricists

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            composers = obj.get("composers")
            lyricists = obj.get("lyricists")
            return Contributors([co for co in composers] if composers else None,
                                [ly for ly in lyricists] if lyricists else None)
        else:
            return Contributors()

    def to_dict(self):
        result = {"composers": [co for co in self.composers] if self.composers else None,
                  "lyricists": [ly for ly in self.lyricists] if self.lyricists else None
                  }
        return result


class Lyrics:
    def __init__(self, copyrights=None):
        self.copyrights = copyrights

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            copyrights = obj.get("copyrights")
            return Lyrics([c for c in copyrights] if copyrights else None)
        else:
            return Lyrics()

    def to_dict(self):
        result = {"copyrights": [c for c in self.copyrights] if self.copyrights else None
                  }
        return result


class Music:
    def __init__(self,
                 external_ids=None,
                 sample_begin_time_offset_ms=None,
                 sample_end_time_offset_ms=None,
                 label=None,
                 duration_ms=None,
                 acrid=None,
                 db_begin_time_offset_ms=None,
                 play_offset_ms=None,
                 release_date=None,
                 genres=None,
                 score=None,
                 title=None,
                 external_metadata=None,
                 album=None,
                 db_end_time_offset_ms=None,
                 result_from=None,
                 artists=None,
                 contributors=None,
                 lyrics=None,
                 language=None):
        self.external_ids = external_ids
        self.sample_begin_time_offset_ms = sample_begin_time_offset_ms
        self.sample_end_time_offset_ms = sample_end_time_offset_ms
        self.label = label
        self.duration_ms = duration_ms
        self.acrid = acrid
        self.db_begin_time_offset_ms = db_begin_time_offset_ms
        self.play_offset_ms = play_offset_ms
        self.release_date = release_date
        self.genres = genres
        self.score = score
        self.title = title
        self.external_metadata = external_metadata
        self.album = album
        self.db_end_time_offset_ms = db_end_time_offset_ms
        self.result_from = result_from
        self.artists = artists
        self.contributors = contributors
        self.lyrics = lyrics
        self.language = language

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            external_ids = ExternalIDS.from_dict(obj.get("external_ids"))
            sample_begin_time_offset_ms = obj.get("sample_begin_time_offset_ms")
            sample_end_time_offset_ms = obj.get("sample_end_time_offset_ms")
            label = obj.get("label")
            duration_ms = obj.get("duration_ms")
            acrid = obj.get("acrid")
            db_begin_time_offset_ms = obj.get("db_begin_time_offset_ms")
            play_offset_ms = obj.get("play_offset_ms")
            release_date = obj.get("release_date")
            genres = [Item.from_dict(g) for g in obj.get("genres")] if obj.get("genres") else None
            score = obj.get("score")
            title = obj.get("title")
            external_metadata = ExternalMetadata.from_dict(obj.get("external_metadata"))
            album = Item.from_dict(obj.get("album"))
            db_end_time_offset_ms = obj.get("db_end_time_offset_ms")
            result_from = obj.get("result_from")
            artists = [Item.from_dict(a) for a in obj.get("artists")] if obj.get("artists") else None
            contributors = Contributors.from_dict(obj.get("contributors"))
            lyrics = Lyrics.from_dict(obj.get("lyrics"))
            language = obj.get("language")

            return Music(external_ids, sample_begin_time_offset_ms, sample_end_time_offset_ms, label, duration_ms,
                         acrid,
                         db_begin_time_offset_ms, play_offset_ms, release_date, genres, score, title, external_metadata,
                         album, db_end_time_offset_ms, result_from, artists, contributors, lyrics, language)
        else:
            return None

    def to_dict(self):
        result = {"external_ids": ExternalIDS.to_dict(self.external_ids) if self.external_ids else None,
                  "sample_begin_time_offset_ms": self.sample_begin_time_offset_ms,
                  "sample_end_time_offset_ms": self.sample_end_time_offset_ms,
                  "label": self.label,
                  "duration_ms": self.duration_ms,
                  "acrid": self.acrid,
                  "db_begin_time_offset_ms": self.db_begin_time_offset_ms,
                  "play_offset_ms": self.play_offset_ms,
                  "release_date": self.release_date,
                  "genres": [g.to_dict() for g in self.genres] if self.genres else None,
                  "score": self.score,
                  "title": self.title,
                  "external_metadata": self.external_metadata.to_dict() if self.external_metadata else None,
                  "album": self.album.to_dict() if self.album else None,
                  "db_end_time_offset_ms": self.db_end_time_offset_ms,
                  "result_from": self.result_from,
                  "artists": [a.to_dict() for a in self.artists] if self.artists else None,
                  "contributors": self.contributors.to_dict() if self.contributors else None,
                  "lyrics": self.lyrics.to_dict() if self.lyrics else None,
                  "language": self.language
                  }
        return result


class CustomFile:
    def __init__(self,
                 audio_id=None,
                 bucket_id=None,
                 duration_ms=None,
                 sample_begin_time_offset_ms=None,
                 sample_end_time_offset_ms=None,
                 title=None,
                 db_end_time_offset_ms=None,
                 db_begin_time_offset_ms=None,
                 acrid=None,
                 play_offset_ms=None,
                 score=None
                 ):
        self.audio_id = audio_id
        self.bucket_id = bucket_id
        self.duration_ms = duration_ms
        self.sample_begin_time_offset_ms = sample_begin_time_offset_ms
        self.sample_end_time_offset_ms = sample_end_time_offset_ms
        self.title = title
        self.db_end_time_offset_ms = db_end_time_offset_ms
        self.db_begin_time_offset_ms = db_begin_time_offset_ms
        self.acrid = acrid
        self.play_offset_ms = play_offset_ms
        self.score = score

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    @staticmethod
    def from_dict(obj):
        if obj:
            audio_id = obj.get("audio_id")
            bucket_id = obj.get("bucket_id")
            duration_ms = obj.get("duration_ms")
            sample_begin_time_offset_ms = obj.get("sample_begin_time_offset_ms")
            sample_end_time_offset_ms = obj.get("sample_end_time_offset_ms")
            title = obj.get("title")
            db_end_time_offset_ms = obj.get("db_end_time_offset_ms")
            db_begin_time_offset_ms = obj.get("db_begin_time_offset_ms")
            acrid = obj.get("acrid")
            play_offset_ms = obj.get("play_offset_ms")
            score = obj.get("score")

            return CustomFile(audio_id, bucket_id, duration_ms, sample_begin_time_offset_ms,
                              sample_end_time_offset_ms, title, db_end_time_offset_ms, db_begin_time_offset_ms, acrid,
                              play_offset_ms, score)
        else:
            return CustomFile()

    def to_dict(self):
        result = {"audio_id": self.audio_id,
                  "bucket_id": self.bucket_id,
                  "duration_ms": self.duration_ms,
                  "sample_begin_time_offset_ms": self.sample_begin_time_offset_ms,
                  "sample_end_time_offset_ms": self.sample_end_time_offset_ms,
                  "title": self.title,
                  "db_end_time_offset_ms": self.db_end_time_offset_ms,
                  "db_begin_time_offset_ms": self.db_begin_time_offset_ms,
                  "acrid": self.acrid,
                  "play_offset_ms": self.play_offset_ms,
                  "score": self.score
                  }
        return result


class BaseResult:
    def __init__(self,
                 filename=None,
                 status_code=None,
                 start_time_ms=None,
                 end_time_ms=None,
                 duration_ms=None,
                 played_duration_ms=None,
                 title=None,
                 score=None,
                 acrid=None,
                 sample_begin_time_offset_ms=None,
                 sample_end_time_offset_ms=None,
                 db_begin_time_offset_ms=None,
                 db_end_time_offset_ms=None):
        self.filename = filename
        self.status_code = status_code
        self.start_time_ms = start_time_ms
        self.end_time_ms = end_time_ms
        self.duration_ms = duration_ms
        self.played_duration_ms = played_duration_ms
        self.title = title
        self.score = score
        self.acrid = acrid
        self.sample_begin_time_offset_ms = sample_begin_time_offset_ms
        self.sample_end_time_offset_ms = sample_end_time_offset_ms
        self.db_begin_time_offset_ms = db_begin_time_offset_ms
        self.db_end_time_offset_ms = db_end_time_offset_ms

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )


class MusicResult(BaseResult):

    def __init__(self,
                 artists_names=None,
                 isrc=None,
                 upc=None,
                 spotify_id=None,
                 youtube_id=None,
                 deezer_id=None,
                 release_date=None,
                 label=None,
                 composers=None,
                 lyricists=None,
                 lyrics=None,
                 language=None,
                 primary_result=None,
                 similar_results=None,
                 filename=None,
                 status_code=None,
                 start_time_ms=None,
                 end_time_ms=None,
                 duration_ms=None,
                 played_duration_ms=None,
                 title=None,
                 score=None,
                 acrid=None,
                 sample_begin_time_offset_ms=None,
                 sample_end_time_offset_ms=None,
                 db_begin_time_offset_ms=None,
                 db_end_time_offset_ms=None):
        super().__init__(filename, status_code, start_time_ms, end_time_ms, duration_ms, played_duration_ms, title,
                         score, acrid, sample_begin_time_offset_ms, sample_end_time_offset_ms, db_begin_time_offset_ms,
                         db_end_time_offset_ms)
        self.artists_names = artists_names
        self.isrc = isrc
        self.upc = upc
        self.spotify_id = spotify_id
        self.youtube_id = youtube_id
        self.deezer_id = deezer_id
        self.release_date = release_date
        self.label = label
        self.composers = composers
        self.lyricists = lyricists
        self.lyrics = lyrics
        self.language = language
        self.primary_result = primary_result
        self.similar_results = similar_results

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def to_dict(self):
        result = {"filename": self.filename,
                  "status_code": self.status_code,
                  "start_time_ms": self.start_time_ms,
                  "end_time_ms": self.end_time_ms,
                  "duration_ms": self.duration_ms,
                  "played_duration_ms": self.played_duration_ms,
                  "title": self.title,
                  "score": self.score,
                  "similar_results": [sr.to_dict() for sr in self.similar_results] if self.similar_results else None,
                  "artists_names": self.artists_names,
                  "isrc": self.isrc,
                  "upc": self.upc,
                  "spotify_id": self.spotify_id,
                  "youtube_id": self.youtube_id,
                  "deezer_id": self.deezer_id,
                  "release_date": self.release_date,
                  "label": self.label,
                  "acrid": self.acrid,
                  "composers": self.composers,
                  "lyricists": self.composers,
                  "lyrics": self.lyrics,
                  "language": self.language,
                  "sample_begin_time_offset_ms": self.sample_begin_time_offset_ms,
                  "sample_end_time_offset_ms": self.sample_end_time_offset_ms,
                  "db_begin_time_offset_ms": self.db_begin_time_offset_ms,
                  "db_end_time_offset_ms": self.db_end_time_offset_ms,
                  }
        return result


class CustomFileResult(BaseResult):
    def __init__(self,
                 similar_results=None,
                 audio_id=None,
                 bucket_id=None,
                 acrid=None,
                 primary_result=None,
                 filename=None,
                 status_code=None,
                 start_time_ms=None,
                 end_time_ms=None,
                 duration_ms=None,
                 played_duration_ms=None,
                 title=None,
                 score=None,
                 sample_begin_time_offset_ms=None,
                 sample_end_time_offset_ms=None,
                 db_begin_time_offset_ms=None,
                 db_end_time_offset_ms=None):
        super().__init__(filename, status_code, start_time_ms, end_time_ms, duration_ms, played_duration_ms, title,
                         score, acrid, sample_begin_time_offset_ms, sample_end_time_offset_ms, db_begin_time_offset_ms,
                         db_end_time_offset_ms)
        self.similar_results = similar_results
        self.audio_id = audio_id
        self.bucket_id = bucket_id
        self.acrid = acrid
        self.primary_result = primary_result

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )

    def to_dict(self):
        result = {"filename": self.filename,
                  "status_code": self.status_code,
                  "start_time_ms": self.start_time_ms,
                  "end_time_ms": self.end_time_ms,
                  "duration_ms": self.duration_ms,
                  "played_duration_ms": self.played_duration_ms,
                  "title": self.title,
                  "score": self.score,
                  "similar_results": [sr.to_dict() for sr in self.similar_results] if self.similar_results else None,
                  "audio_id": self.audio_id,
                  "bucket_id": self.bucket_id,
                  "acrid": self.acrid,
                  "sample_begin_time_offset_ms": self.sample_begin_time_offset_ms,
                  "sample_end_time_offset_ms": self.sample_end_time_offset_ms,
                  "db_begin_time_offset_ms": self.db_begin_time_offset_ms,
                  "db_end_time_offset_ms": self.db_end_time_offset_ms,
                  }
        return result


def response_from_dict(s):
    return Response.from_dict(s)


def response_to_dict(x):
    return Response.to_dict(x)
