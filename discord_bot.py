import os
import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from models import db, Note, Warning, ModAction, Score
from flask import Flask

TOKEN = os.environ.get("DISCORD_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")  # e.g., sqlite:///bot.db

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="...", intents=intents)

# Flask app for DB context
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# -----------------------------
# Example: warn command
# -----------------------------
@bot.command()
async def warn(ctx, user: discord.Member, weight: int = 1, *, reason="No reason provided"):
    with app.app_context():
        warn_count = Warning.query.filter_by(user_id=str(user.id)).count() + 1
        punishment_list = ["3h mute", "6h mute", "24h mute", "72h mute", "ban"]
        punishment = punishment_list[min(warn_count-1, len(punishment_list)-1)]

        warning = Warning(
            user_id=str(user.id),
            reason=reason,
            weight=weight,
            punishment=punishment,
            moderator=str(ctx.author),
            time=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(warning)
        db.session.commit()

        # Update score
        score = Score.query.filter_by(user_id=str(user.id)).first()
        if not score:
            score = Score(user_id=str(user.id), points=0)
            db.session.add(score)
        score.points -= 10 * weight
        db.session.commit()

    await ctx.send(f"{user.mention} warned for '{reason}'. Suggested punishment: {punishment}")

# -----------------------------
# Weekly score updater
# -----------------------------
@tasks.loop(hours=168)
async def weekly_score_update():
    with app.app_context():
        now = datetime.utcnow()
        scores = Score.query.all()
        for s in scores:
            if (now - s.last_updated).days >= 7:
                s.points += 5
                s.last_updated = now
        db.session.commit()

@bot.event
async def on_ready():
    weekly_score_update.start()
    print(f"Bot ready: {bot.user}")

bot.run(TOKEN)
