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
    await asyncio.sleep(10)
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
        # Skip the empty row and get movies from row 2 down
    movie_list = sheet.col_values(1)[1:]  # Start from row 2 to skip the empty row
    user_list = sheet.row_values(2)  # User headers are on row 2                     #user_list = ["Movie", "thombo10", "samelpo", "AVG Rating"]

    for reaction in message.reactions:
        if str(reaction.emoji) in reactions_map:
            # users = [user async for user in reaction.users()] #all user who reacted to that reaction
            async for user in reaction.users():
            # for user in users:
                if user != bot.user:  #Ignore the bot's vote  
                    
                    currenthighest = reactions_map[str(reaction.emoji)] #emoji = 3ect 
                    if str(user) in poll_data["votes"]:
                        poll_data["votes"][str(user)] = max(poll_data["votes"][str(user)], currenthighest)
                    else: 
                        poll_data["votes"][str(user)] = currenthighest  

    if movie in movie_list:
        row = movie_list.index(movie) + 2 
    else:
        row = len(movie_list) + 2  
        sheet.update_cell(row, 1, movie)  


    for user, rating in poll_data["votes"].items():
        if user in user_list:
            col = user_list.index(user) + 1
        else:
            avg_rating_col = user_list.index("AVG Rating") + 1   ##user_list = ["Movie", "thombo10", "samelpo", "AVG Rating"] , user_list.index("Average Rating") = 3 starst at zeros
            sheet.insert_cols([[None]], avg_rating_col)  #empty column instead inserting the username in the first row. now one below error fix 
            sheet.update_cell(2, avg_rating_col, user)  # Place "user" in row 2 instead of row 1
    


            #sheet.insert_cols([[user]], avg_rating_col) # plcae the new user where rating was and shift the rest to the right


            user_list.insert(avg_rating_col-1,user)#update list after adding new user to collumn ? 
            col = avg_rating_col
        sheet.update_cell(row, col, rating)

            





    await ctx.send(f"✅ The poll for **{movie}** has ended. Ratings have been saved to the Google Sheet!")

    del active_polls[message.id]




bot.run(DISCORD_TOKEN)
