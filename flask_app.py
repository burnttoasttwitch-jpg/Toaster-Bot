import os
from flask import Flask, render_template
from models import db, Note, Warning, ModAction, Score

DATABASE_URL = os.environ.get("DATABASE_URL")
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def dashboard():
    scores = Score.query.order_by(Score.points.desc()).all()
    return render_template("dashboard.html", scores=scores)

@app.route("/user/<user_id>")
def user_page(user_id):
    notes = Note.query.filter_by(user_id=user_id).all()
    warns = Warning.query.filter_by(user_id=user_id).all()
    actions = ModAction.query.filter_by(user_id=user_id).all()
    score = Score.query.filter_by(user_id=user_id).first()
    return render_template("user.html", notes=notes, warns=warns, actions=actions, score=score)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
