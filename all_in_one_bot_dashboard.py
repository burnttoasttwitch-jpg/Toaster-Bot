import threading
from datetime import datetime, timedelta

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

import discord
from discord.ext import commands, tasks

# ------------------------
# CONFIGURATION
# ------------------------
DISCORD_TOKEN = "MTM5NjQ3ODQ0ODEwODU3Mjc2Mw.GrydSM.ZqIk5VbN0nIOe6Ty9dOyaH7ALWybrmGZCvLy3c"
BOT_PREFIX = "..."
DB_PATH = "sqlite:///bot.db"

# ------------------------
# FLASK DASHBOARD SETUP
# ------------------------
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ------------------------
# DATABASE MODELS
# ------------------------
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    moderator = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    moderator = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    weight = db.Column(db.Integer, default=1)
    expires_at = db.Column(db.DateTime, nullable=True)

class ModAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    action = db.Column(db.String(80), nullable=False)
    moderator = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Score(db.Model):
    user_id = db.Column(db.String(80), primary_key=True)
    points = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

db.create_all()

# ------------------------
# DASHBOARD ROUTES
# ------------------------
@app.route("/")
def index():
    users = Score.query.all()
    return render_template("dashboard.html", users=users)

@app.route("/user/<user_id>")
def user_page(user_id):
    notes = Note.query.filter_by(user_id=user_id).all()
    warnings = Warning.query.filter_by(user_id=user_id).all()
    actions = ModAction.query.filter_by(user_id=user_id).all()
    score = Score.query.filter_by(user_id=user_id).first()
    return render_template(
        "user.html",
        user_id=user_id,
        notes=notes,
        warnings=warnings,
        actions=actions,
        score=score.points if score else 0
    )

def run_flask():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_flask, daemon=True).start()

# ------------------------
# DISCORD BOT SETUP
# ------------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)

punishments = ["3h mute", "6h mute", "24h mute", "72h mute", "ban"]

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def get_score(user_id):
    score = Score.query.filter_by(user_id=user_id).first()
    if not score:
        score = Score(user_id=user_id, points=0)
        db.session.add(score)
        db.session.commit()
    return score

def update_score_on_warn(user_id, weight=1):
    score = get_score(user_id)
    score.points -= 10 + (weight - 1) * 10
    score.last_updated = datetime.utcnow()
    db.session.commit()

def update_score_on_action(user_id, action_type):
    score = get_score(user_id)
    if action_type == "mute":
        score.points -= 5
    elif action_type == "ban":
        score.points -= 100
    score.last_updated = datetime.utcnow()
    db.session.commit()

def add_weekly_points():
    now = datetime.utcnow()
    scores = Score.query.all()
    for s in scores:
        last = s.last_updated or datetime.utcnow()
        if (now - last).days >= 7:
            s.points += 5
            s.last_updated = now
    db.session.commit()

# ------------------------
# BACKGROUND TASKS
# ------------------------
@tasks.loop(hours=24)
async def weekly_score_update():
    add_weekly_points()

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    weekly_score_update.start()

# ------------------------
# NOTE COMMANDS
# ------------------------
@bot.command()
async def note(ctx, user: discord.Member, *, text: str):
    n = Note(user_id=str(user.id), content=text, moderator=str(ctx.author))
    db.session.add(n)
    db.session.commit()
    await ctx.send(f"📝 Note added for {user.display_name}.")

@bot.command(name="notes")
async def notes_cmd(ctx, user: discord.Member):
    notes = Note.query.filter_by(user_id=str(user.id)).all()
    if not notes:
        await ctx.send(f"ℹ️ No notes for {user.display_name}.")
        return
    msg = f"📒 Notes for {user.display_name}:\n"
    for n in notes:
        msg += f"- {n.content} (by {n.moderator} at {n.timestamp})\n"
    await ctx.send(msg)

@bot.command()
async def delnote(ctx, user: discord.Member, note_id: int):
    note = Note.query.filter_by(id=note_id, user_id=str(user.id)).first()
    if note:
        db.session.delete(note)
        db.session.commit()
        await ctx.send(f"🗑️ Note #{note_id} deleted for {user.display_name}.")
    else:
        await ctx.send(f"⚠️ Note not found.")

# ------------------------
# WARN COMMANDS
# ------------------------
@bot.command()
async def warn(ctx, user: discord.Member, weight: int = 1, *, reason: str = "No reason provided"):
    w = Warning(
        user_id=str(user.id),
        reason=reason,
        moderator=str(ctx.author),
        weight=weight,
        expires_at=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(w)
    db.session.commit()
    update_score_on_warn(str(user.id), weight)
    await ctx.send(f"⚠️ Warning issued to {user.display_name}: {reason} (Weight {weight})")

@bot.command(name="warns")
async def warns_cmd(ctx, user: discord.Member):
    warnings = Warning.query.filter_by(user_id=str(user.id)).all()
    if not warnings:
        await ctx.send(f"ℹ️ No warnings for {user.display_name}.")
        return
    msg = f"⚠️ Warnings for {user.display_name}:\n"
    for w in warnings:
        msg += f"- {w.reason} by {w.moderator} at {w.timestamp}\n"
    await ctx.send(msg)

@bot.command()
async def delwarn(ctx, user: discord.Member, warn_id: int):
    w = Warning.query.filter_by(id=warn_id, user_id=str(user.id)).first()
    if w:
        db.session.delete(w)
        db.session.commit()
        score = get_score(str(user.id))
        score.points += 10 + (w.weight - 1) * 10
        db.session.commit()
        await ctx.send(f"🗑️ Warning #{warn_id} deleted for {user.display_name}.")
    else:
        await ctx.send(f"⚠️ Warning not found.")

# ------------------------
# MOD ACTIONS
# ------------------------
@bot.command()
async def modaction(ctx, user: discord.Member, action_type: str, *, reason: str = "No reason provided"):
    ma = ModAction(user_id=str(user.id), action=action_type, moderator=str(ctx.author))
    db.session.add(ma)
    db.session.commit()
    update_score_on_action(str(user.id), action_type)
    await ctx.send(f"🛠️ Mod action '{action_type}' applied to {user.display_name}.")

# ------------------------
# USER SCORE
# ------------------------
@bot.command()
async def myscore(ctx):
    score = get_score(str(ctx.author.id))
    await ctx.send(f"💯 {ctx.author.display_name}, your current score is: {score.points}")

# ------------------------
# RUN BOT
# ------------------------
bot.run("MTM5NjQ3ODQ0ODEwODU3Mjc2Mw.GrydSM.ZqIk5VbN0nIOe6Ty9dOyaH7ALWybrmGZCvLy3c")
