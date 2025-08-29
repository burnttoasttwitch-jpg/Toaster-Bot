from flask import Flask, render_template
from database import SessionLocal, engine, Base
from models import User

# Make sure all tables exist
Base.metadata.create_all(bind=engine)

app = Flask(__name__)

# Home route -> dashboard
@app.route("/")
def home():
    session = SessionLocal()
    # Pull all users to display on dashboard
    all_users = session.query(User).all()
    session.close()
    return render_template("dashboard.html", users=all_users)

# List all users
@app.route("/users")
def users():
    session = SessionLocal()
    all_users = session.query(User).all()
    session.close()
    return render_template("users.html", users=all_users)

# User detail page
@app.route("/user/<int:user_id>")
def user_detail(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return render_template("user.html", user=user)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
