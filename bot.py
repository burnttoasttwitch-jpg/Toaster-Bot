import discord
from discord.ext import commands
from database import SessionLocal
from models import User

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="...", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

# Example: Command that updates user points
@bot.command()
async def addpoints(ctx, user_id: int, points: int):
    session = SessionLocal()
    user = session.query(User).filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id, points=0)
        session.add(user)
    user.points += points
    session.commit()
    session.close()
    await ctx.send(f"Added {points} points to {user_id}!")

if __name__ == "__main__":
    TOKEN = "DISCORD_TOKEN"
    bot.run(TOKEN)
