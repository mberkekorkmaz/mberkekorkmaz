from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///restaurants.db")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    cuisine = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(200), nullable=False)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurant.id"), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    restaurant = db.relationship("Restaurant", backref=db.backref("comments", lazy=True))


@app.route("/restaurants", methods=["GET"])
def list_restaurants():
    cuisine = request.args.get("cuisine")
    query = Restaurant.query
    if cuisine:
        query = query.filter_by(cuisine=cuisine)
    restaurants = query.all()
    return jsonify([
        {"id": r.id, "name": r.name, "cuisine": r.cuisine, "location": r.location}
        for r in restaurants
    ])


@app.route("/restaurants", methods=["POST"])
def create_restaurant():
    data = request.get_json() or {}
    if not all(k in data for k in ("name", "cuisine", "location")):
        return {"error": "Missing fields"}, 400
    restaurant = Restaurant(name=data["name"], cuisine=data["cuisine"], location=data["location"])
    db.session.add(restaurant)
    db.session.commit()
    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "cuisine": restaurant.cuisine,
        "location": restaurant.location,
    }, 201


@app.route("/restaurants/<int:restaurant_id>/comments", methods=["GET"])
def list_comments(restaurant_id):
    comments = Comment.query.filter_by(restaurant_id=restaurant_id).all()
    return jsonify([
        {"id": c.id, "author": c.author, "content": c.content} for c in comments
    ])


@app.route("/restaurants/<int:restaurant_id>/comments", methods=["POST"])
def add_comment(restaurant_id):
    data = request.get_json() or {}
    if not all(k in data for k in ("author", "content")):
        return {"error": "Missing fields"}, 400
    comment = Comment(restaurant_id=restaurant_id, author=data["author"], content=data["content"])
    db.session.add(comment)
    db.session.commit()
    return {"id": comment.id, "author": comment.author, "content": comment.content}, 201


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
