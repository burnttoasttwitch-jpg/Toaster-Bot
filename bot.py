import discord
from discord.ext import commands
from database import SessionLocal, engine, Base
from models import User, Warning, Note

Base.metadata.create_all(bind=engine)
bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

def get_or_create_user(session, discord_id):
    user = session.query(User).filter_by(discord_id=str(discord_id)).first()
    if not user:
        user = User(discord_id=str(discord_id))
        session.add(user)
        session.commit()
    return user

@bot.command()
async def warn(ctx, member: discord.Member, *, reason: str):
    session = SessionLocal()
    user = get_or_create_user(session, member.id)
    warning = Warning(reason=reason, user=user)
    session.add(warning)
    session.commit()
    await ctx.send(f"⚠️ {member.mention} has been warned: {reason}")
    session.close()

@bot.command()
async def warnings(ctx, member: discord.Member):
    session = SessionLocal()
    user = get_or_create_user(session, member.id)
    if not user.warnings:
        await ctx.send(f"{member.mention} has no warnings.")
    else:
        msg = "\n".join([f"{i+1}. {w.reason}" for i, w in enumerate(user.warnings)])
        await ctx.send(f"Warnings for {member.mention}:\n{msg}")
    session.close()

@bot.command()
async def notes_add(ctx, member: discord.Member, *, note: str):
    session = SessionLocal()
    user = get_or_create_user(session, member.id)
    new_note = Note(content=note, user=user)
    session.add(new_note)
    session.commit()
    await ctx.send(f"📝 Note added for {member.mention}")
    session.close()

@bot.command()
async def notes_list(ctx, member: discord.Member):
    session = SessionLocal()
    user = get_or_create_user(session, member.id)
    if not user.notes:
        await ctx.send(f"{member.mention} has no notes.")
    else:
        msg = "\n".join([f"{i+1}. {n.content}" for i, n in enumerate(user.notes)])
        await ctx.send(f"Notes for {member.mention}:\n{msg}")
    session.close()

bot.run("YOUR_DISCORD_BOT_TOKEN")
