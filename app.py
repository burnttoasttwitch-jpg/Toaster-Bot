# app.py
from flask import Flask, render_template
from database import SessionLocal, engine, Base
from models import User
import threading
import asyncio
import discord
from discord.ext import commands

# --- Flask Setup ---
Base.metadata.create_all(bind=engine)
app = Flask(__name__)

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

@app.route("/")
def home():
    session = SessionLocal()
    all_users = session.query(User).all()
    session.close()
    return render_template("dashboard.html", users=all_users)

def run_flask():
    # Run Flask in a thread
    app.run(host="0.0.0.0", port=5000, debug=False)

# --- Discord Bot Setup ---
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Example command
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# --- Main ---
if __name__ == "__main__":
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Run Discord bot in main thread
    TOKEN = "BOT_TOKEN"
    bot.run(TOKEN)
