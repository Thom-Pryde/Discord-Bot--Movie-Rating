from discord.ext import commands
import discord
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)
sheet = client.open("DiscordBot").sheet1

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
active_polls = {}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.command()
async def MovieTime (ctx, *, movie:str):

    message= await ctx.send(f"**Hello crodies!** We just watched {movie}, please react below to rate the movie" "\1️⃣ - 1 Star"
        "\2️⃣ - 2 Stars"
        "\3️⃣ - 3 Stars"
        "\4️⃣ - 4 Stars"
        "\5️⃣ - 5 Stars"
    )

    # reactions = ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]

    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]



    for reaction in reactions:
        await message.add_reaction(reaction)

 
    active_polls[message.id] = {"movie": movie, "votes": {}}
    await asyncio.sleep(30)
    await collect_votes(ctx, message)


#{"movie": movie, "votes": {}}
#{"movie": movie, "votes": {"dbax12":4, "thombo10":5"}}
async def collect_votes(ctx, message):
    poll_data = active_polls.get(message.id)    #get to see if the poll is still goign n hasnt finshed sleeping
    if not poll_data:
        return  

    movie = poll_data["movie"]
    message = await ctx.channel.fetch_message(message.id)#newest message
    # reactions_map = {"⭐": 1, "⭐⭐": 2, "⭐⭐⭐": 3, "⭐⭐⭐⭐": 4, "⭐⭐⭐⭐⭐": 5}
    reactions_map = {
    "1️⃣": 1,
    "2️⃣": 2,
    "3️⃣": 3,
    "4️⃣": 4,
    "5️⃣": 5}

#poll_data = {
#     "movie": "Avatar",
#     "votes": {
#         "thombo": 4,
#         "samelpo": 5
#     }
# }

    # for reaction in message.reactions:
    #     if str(reaction.emoji) in reactions_map:
    #         # users = await reaction.users().flatten()  
    #         # for user in users:
    #         users = [user async for user in reaction.users()]
    #         for user in users:
    #             if user != bot.user:  #Ignore the bot's vote  
                    
    #                 rating = reactions_map[str(reaction.emoji)] #emoji = 3ect 
    #                 poll_data["votes"][str(user)] = rating  
    for reaction in message.reactions:
        if str(reaction.emoji) in reactions_map:
            users = [user async for user in reaction.users()] #all user who reacted to that reaction
            for user in users:
                if user != bot.user:  #Ignore the bot's vote  
                    
                    currenthighest = reactions_map[str(reaction.emoji)] #emoji = 3ect 
                    if str(user) in poll_data["votes"]:
                        poll_data["votes"][str(user)] = max(poll_data["votes"][str(user)], currenthighest)
                    else: 
                        poll_data["votes"][str(user)] = currenthighest  

    
    for user, rating in poll_data["votes"].items():
        sheet.append_row([user, movie, rating])

    await ctx.send(f"✅ The poll for **{movie}** has ended. Ratings have been saved to the Google Sheet!")

    # Clean poll data
    del active_polls[message.id]


bot.run(DISCORD_TOKEN)
