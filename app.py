from flask import Flask, render_template
from database import SessionLocal, Base, engine
from models import User

# Create tables if they don't exist yet
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

@app.route("/")
def dashboard():
    session = SessionLocal()
    all_users = session.query(User).all()
    session.close()
    return render_template("dashboard.html", users=all_users)

@app.route("/users")
def users():
    session = SessionLocal()
    all_users = session.query(User).all()
    session.close()
    return render_template("users.html", users=all_users)

@app.route("/user/<int:user_id>")
def user_detail(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return render_template("user.html", user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
