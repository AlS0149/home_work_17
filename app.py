from flask import Flask, request  # Импортируем необходимые библиотеки, модули и пакеты
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)  # Регистрируем приложение, указываем настройки подключения к БД
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


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


class Director(db.Model):

    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):

    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):

    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

db.create_all()


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):


        dir_id = request.args.get('director_id')
        gen_id = request.args.get('genre_id')

        if dir_id is None and gen_id is None:
            result = Movie.query.all()
            if result:
                return movies_schema.dump(result), 200
            else:
                return "Данных нет", 404

        elif dir_id and gen_id is None:
            result = db.session.query(Movie).filter(Movie.director_id == int(dir_id)).all()
            if result:
                return movies_schema.dump(result), 200
            else:
                return "Данных нет", 404

        elif gen_id and dir_id is None:
            result = db.session.query(Movie).filter(Movie.genre_id == int(gen_id)).all()
            if result:
                return movies_schema.dump(result), 200
            else:
                return "Данных нет", 404

        else:
            result = db.session.query(Movie).filter(Movie.genre_id == int(gen_id), Movie.director_id == int(dir_id)).all()
            if result:
                return movies_schema.dump(result), 200
            else:
                return "Данных нет", 404


@movie_ns.route('/<int:mid>')
class MovieView(Resource):

    def get(self, mid):

        movie = Movie.query.get(mid)
        if movie:
            return movie_schema.dump(movie), 200
        else:
            return "Данных нет", 404


@director_ns.route('/')
class DirectorView(Resource):

    def post(self):

        try:
            data = request.json
            new_dir = Director(**data)
            with db.session.begin():
                db.session.add(new_dir)
            return "", 201
        except Exception as e:
            return str(e), 404


@director_ns.route('/<int:did>')
class DirectorView(Resource):

    def put(self, did):

        director = Director.query.get(did)
        if not director:
            return "", 404

        request_data = request.json
        director.id = request_data.get('id')
        director.name = request_data.get('name')
        with db.session.begin():
            db.session.add(director)
        return "", 204

    def delete(self, did):

        director = Director.query.get(did)
        if not director:
            return "", 404

        with db.session.begin():
            db.session.delete(director)
        return "", 204


@genre_ns.route('/')  # Представление по маршруту '/Genre/'
class GenreView(Resource):

    def post(self):

        try:
            data = request.json
            new_gen = Genre(**data)
            with db.session.begin():
                db.session.add(new_gen)
            return "", 201
        except Exception as e:
            return str(e), 404


@genre_ns.route('/<int:gid>')  # Представление по маршруту '/Genre/id'
class GenreView(Resource):

    def put(self, gid):
        gen = Genre.query.get(gid)
        if not gen:
            return "", 404

        request_data = request.json
        gen.id = request_data.get('id')
        gen.name = request_data.get('name')
        with db.session.begin():
            db.session.add(gen)
        return "", 204

    def delete(self, gid):
        gen = Genre.query.get(gid)
        if not gen:
            return "", 404

        with db.session.begin():
            db.session.delete(gen)
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
