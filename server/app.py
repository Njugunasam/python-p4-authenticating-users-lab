#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

# Ensure that the session persists across requests
@app.before_request
def before_request():
    session.permanent = True

class ClearSession(Resource):
    def delete(self):
        # Clear session variables
        session.pop('page_views', None)
        session.pop('user_id', None)

        return {}, 204

class IndexArticle(Resource):
    def get(self):
        # Get all articles
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class ShowArticle(Resource):
    def get(self, id):
        # Initialize page views if not present in session
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        # Check page view limit
        if session['page_views'] <= 3:
            # Get article by ID
            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())
            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            username = data.get('username')

            user = User.query.filter(User.username == username).first()

            if user:
                session['user_id'] = user.id
                return jsonify(user.to_dict()), 200
            else:
                return {'message': 'User not found'}, 404
        except Exception as e:
            return {'message': 'Error during login'}, 500

class Logout(Resource):
    def delete(self):
        try:
            session.pop('user_id', None)
            return {}, 204
        except Exception as e:
            return {'message': 'Error during logout'}, 500

class CheckSession(Resource):
    def get(self):
        try:
            user_id = session.get('user_id')

            if user_id:
                user = User.query.get(user_id)
                return jsonify(user.to_dict()), 200
            else:
                return {}, 401
        except Exception as e:
            return {'message': 'Error during session check'}, 500

api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
