# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app. config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}

db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float( )
    genre_id = fields.Int( )
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)



api = Api(app)
movie_ns = api.namespace('movies')
#movie_by_dir_ns = api.namespace('movie_by_dir')
#movie_by_genre_ns = api.namespace('movie_by_genre')
#movie_by_genre_dir_ns = api.namespace('movie_by_genre_dir')
director_ns = api.namespace('directors')

@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        gid = request.args.get ('genre_id')
        did = request.args.get ('director_id')
        mdg = Movie.query
        if did:
            mdg = mdg.filter(Movie.director_id == did)
        if gid:
            mdg = mdg.filter (Movie.genre_id == gid)
        movies = mdg.all()
        return movies_schema.dump(movies), 200

    def post(self) :
        data = request.json
        new_movie = Movie(**data)
        db.session.add(new_movie)
        db.session.commit()
        return '', 201


@movie_ns.route('/<int:nid>')
class MovieView(Resource):
    def get(self, nid):
        movie = db.session.query(Movie).filter(Movie.id == nid)
        return movies_schema.dump(movie), 200

#@movie_by_dir_ns.route('/')
#class MovieDirector(Resource):
#    def get(self):
#        did = request.args.get('director_id')
#        movies = db.session.query(Movie).filter(Movie.director_id == int(did))
#        return movies_schema.dump(movies), 200

#@movie_by_genre_ns.route('/')
#class MovieDirector(Resource):
#    def get(self):
#        gid = request.args.get('genre_id')
#        movies = db.session.query(Movie).filter(Movie.genre_id == int(gid))
#        return movies_schema.dump(movies), 200

#@movie_by_genre_dir_ns.route('/')
#class MovieDirectorGenre(Resource):
#    def get(self):
#        gid = request.args.get('genre_id')
#        did = request.args.get('director_id')
#        movies = db.session.query(Movie).filter(Movie.genre_id == int(gid), Movie.director_id == int(did))
#        return movies_schema.dump(movies), 200

    def post(self) :
        req_json = request.json
        db.session.add(Director).one(**req_json)
        db.session.commit()
        return "", 204

@director_ns.route('/')
class DirectorView(Resource):
    def get(self):
        directors = Director.query.all()
        return directors_schema.dump(directors), 200

    def post(self) :
        data = request.json
        new_director = Director(**data)
        db.session.add(new_director)
        db.session.commit()
        return '', 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did):
        director = Director.query.get(did)
        return director_schema.dump(director), 200

    def put(self, did):
        director = Director.query.get(did)
        if not director:
            return "", 404
        req_json = request.json
        director.name = req_json.get('name')
        db.session.add(director)
        db.session.commit()
        return "", 204

    def delete(self, did):
        director = Director.query.get (did)
        if not director:
            return "", 404
        db.session.delete(director)
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
