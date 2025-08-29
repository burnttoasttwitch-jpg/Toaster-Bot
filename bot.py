from threading import Thread
from flask import Flask, render_template
from database import SessionLocal, engine, Base
from models import User
from discord.ext import commands

# ---------- Flask Setup ----------
Base.metadata.create_all(bind=engine)
app = Flask(__name__)

@app.route("/")
def home():
    session = SessionLocal()
    all_users = session.query(User).all()
    session.close()
    return render_template("dashboard.html", users=all_users)

@app.route("/user/<int:user_id>")
def user_detail(user_id):
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    session.close()
    return render_template("user.html", user=user)

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True)

# ---------- Discord Bot Setup ----------
bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# ---------- Run Both ----------
if __name__ == "__main__":
    Thread(target=run_flask).start()  # Flask runs in a separate thread
    bot.run("YOUR_DISCORD_TOKEN")     # Bot runs in main thread
