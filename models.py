from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    text = db.Column(db.Text, nullable=False)
    moderator = db.Column(db.String, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, default=1)
    punishment = db.Column(db.String, nullable=False)
    moderator = db.Column(db.String, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

class ModAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=False)
    moderator = db.Column(db.String, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, nullable=False)
    points = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
