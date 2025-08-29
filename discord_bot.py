import os
import discord
from discord.ext import commands
from flask import Flask, render_template, request, redirect, url_for
from threading import Thread
from waitress import serve

# =========================
# DISCORD BOT SETUP
# =========================
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Store warnings/notes in memory (replace with DB later if needed)
warnings = {}
notes = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    user_id = str(member.id)
    warnings.setdefault(user_id, []).append(reason)
    await ctx.send(f"⚠️ {member.display_name} has been warned. Reason: {reason}")

@bot.command()
async def notes_add(ctx, member: discord.Member, *, note):
    user_id = str(member.id)
    notes.setdefault(user_id, []).append(note)
    await ctx.send(f"📝 Note added for {member.display_name}.")

@bot.command()
async def warnings(ctx, member: discord.Member):
    user_id = str(member.id)
    user_warnings = warnings.get(user_id, [])
    if not user_warnings:
        await ctx.send(f"✅ {member.display_name} has no warnings.")
    else:
        await ctx.send(f"⚠️ Warnings for {member.display_name}: " + "; ".join(user_warnings))

@bot.command()
async def notes_list(ctx, member: discord.Member):
    user_id = str(member.id)
    user_notes = notes.get(user_id, [])
    if not user_notes:
        await ctx.send(f"📝 No notes for {member.display_name}.")
    else:
        await ctx.send(f"📝 Notes for {member.display_name}: " + "; ".join(user_notes))


# =========================
# FLASK DASHBOARD SETUP
# =========================
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/users")
def users_page():
    # Pass notes and warnings to frontend
    return render_template("users.html", warnings=warnings, notes=notes)

@app.route("/user/<user_id>")
def user_page(user_id):
    return render_template(
        "user.html",
        user_id=user_id,
        user_warnings=warnings.get(user_id, []),
        user_notes=notes.get(user_id, [])
    )

# =========================
# RUN DISCORD BOT + FLASK TOGETHER
# =========================
def run_flask():
    serve(app, host="0.0.0.0", port=8080)

def run_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
