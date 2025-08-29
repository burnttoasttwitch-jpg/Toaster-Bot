from flask import Flask, render_template
from database import SessionLocal, engine, Base
from models import User

Base.metadata.create_all(bind=engine)
app = Flask(__name__)

@app.route("/users")
def users():
    session = SessionLocal()
    all_users = session.query(User).all()
    return render_template("users.html", users=all_users)

@app.route("/user/<int:user_id>")
def user_detail(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    return render_template("user.html", user=user)
