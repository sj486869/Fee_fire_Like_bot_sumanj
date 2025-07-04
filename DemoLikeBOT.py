import discord
from discord.ext import commands
import requests
import asyncio
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

VIP_USERS = {123456789012345678}  # Optional VIPs
like_request_tracker = {}

API_URL = "https://free-api-like-freefire-red.vercel.app/like?uid="

def call_api(uid):
    try:
        response = requests.get(f"{API_URL}{uid}", timeout=10)
        if response.status_code != 200 or not response.text.strip():
            return None
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

def create_embed(title, description, color):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.utcnow()
    )
    return embed

@bot.command()
async def like(ctx, uid: str = None):
    user_id = ctx.author.id

    # Validation check (only requires digits now)
    if not uid or not uid.isdigit():
        embed = create_embed(
            "❌ Invalid Format",
            "Please use a valid numeric UID\n**Example:** `!like 8385763215`",
            0xe74c3c
        )
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/cross-mark_274c.png")
        return await ctx.send(embed=embed)

    # Cooldown check
    if user_id not in VIP_USERS and like_request_tracker.get(user_id, False):
        embed = create_embed(
            "⏳ Request Limit Reached",
            "You've used your daily request! Try again tomorrow",
            0xf39c12
        )
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/hourglass-not-done_23f3.png")
        return await ctx.send(embed=embed)

    # Start processing
    progress = await ctx.send("🔍 **Processing your request...**")
    steps = [
        "🔄 Contacting game servers...",
        "📡 Verifying UID validity...",
        "🚀 Sending like request...",
        "⏳ Finalizing transaction..."
    ]
    
    for step in steps:
        await asyncio.sleep(1.2)
        await progress.edit(content=step)

    # API call
    response = call_api(uid)
    
    # Handle API failure
    if response is None:
        embed = create_embed(
            "⚠️ Service Unavailable",
            "The like service is currently unavailable\nPlease try again later",
            0xe67e22
        )
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/warning_26a0.png")
        return await progress.edit(content=None, embed=embed)

    # Process response
    status = response.get("status", 0)
    uid_val = response.get("uid", "N/A")
    name = response.get("player", "Unknown Player")
    before = response.get("likes_before", "N/A")
    after = response.get("likes_after", "N/A")
    added = response.get("likes_added", "N/A")
    server = response.get("server_used", "Unknown Server")

    # Update tracker
    if status == 1 and user_id not in VIP_USERS:
        like_request_tracker[user_id] = True

    # Build response embed
    if status == 1:
        embed = create_embed(
            "🎉 Like Added Successfully!",
            f"**{name}** received free likes!",
            0x2ecc71
        )
        fields = [
            ("🆔 UID", uid_val, True),
            ("❤️ Likes Before", before, True),
            ("💚 Likes After", after, True),
            ("📤 Likes Added", added, True),
            ("🌐 Server", server, True)
        ]
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/sparkling-heart_1f496.png")
        
    elif status == 2:
        embed = create_embed(
            "⚠️ Daily Limit Reached",
            f"**{name}** has already received maximum likes today",
            0xf1c40f
        )
        fields = [
            ("🆔 UID", uid_val, True),
            ("❤️ Current Likes", after, True),
            ("⏱️ Next Reset", "Daily Reset (00:00 UTC)", True)
        ]
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/hourglass-done_231b.png")
        
    else:
        embed = create_embed(
            "❌ Unknown Error",
            "Received unexpected response from server",
            0xe74c3c
        )
        fields = [
            ("Status Code", status, False),
            ("UID", uid_val, False)
        ]
        embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/question-mark_2753.png")

    # Add fields to embed
    for name, value, inline in fields:
        embed.add_field(name=name, value=value, inline=inline)
    
    # Final touches
    embed.set_footer(text="FreeFire Like Service • Today at")
    embed.set_author(
        name=ctx.author.display_name,
        icon_url=ctx.author.display_avatar.url
    )
    
    await progress.edit(content=None, embed=embed)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="!like <UID>"
        )
    )

@bot.command()
async def help(ctx):
    embed = create_embed(
        "💎 FreeFire Like Bot Help",
        "Get free in-game likes for FreeFire accounts",
        0x3498db
    )
    embed.add_field(
        name="🚀 How to Use",
        value="```!like <UID>```\nExample: `!like 8385763215`",
        inline=False
    )
    embed.add_field(
        name="⏱️ Limitations",
        value="• 1 request per user daily\n• VIP users have no limits",
        inline=False
    )
    embed.add_field(
        name="🔧 Support",
        value="[Support Server](https://discord.gg/your-invite)",
        inline=False
    )
    embed.set_thumbnail(url="https://em-content.zobj.net/thumbs/160/twitter/348/gem-stone_1f48e.png")
    await ctx.send(embed=embed)


bot.run("MTM5MDYzNjc4MDQ4Njc4NzE1Mw.GddbPV.ZdgBNDfIzB8zfkYnhLwxvVz75JL0ZugYpHZ6QE") 