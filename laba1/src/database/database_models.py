import peewee

from settings import DATABASE_PATH, DEBUG

db = peewee.SqliteDatabase(database=DATABASE_PATH)


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Musics(BaseModel):
    artist = peewee.CharField()
    title = peewee.CharField()
    path = peewee.CharField(unique=True)
    class Meta:
        database = db
        indexes = (
            (('artist', 'title'), True),
        )


class Users(BaseModel):
    password = peewee.CharField()
    username = peewee.CharField(unique=True)


class UserPlaylists(BaseModel):
    user_id = peewee.ForeignKeyField(Users, backref='playlists')
    music_id = peewee.ForeignKeyField(Musics, backref='playlists')
    class Meta:
        database = db
        indexes = (
            (('user_id', 'music_id'), True),
        )


db.create_tables([Musics, Users, UserPlaylists])
        