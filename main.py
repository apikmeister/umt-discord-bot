import discord
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from discord.ext import commands

from embed import *

import db

load_dotenv()
BOT_TOKEN = (os.getenv('BOT_TOKEN'))
GPA_URL = (os.getenv('GPA_URL'))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="your grades"))
    print('Bot is ready')

# add user
@bot.command()
async def login(ctx, *, args=None):
    discord_id = ctx.author.id
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args != None and len(args.split()) == 2:
            username, password = args.split()
            try:  # Check if user exists
                if (db.checkUser(discord_id)):
                    embed = smallEmbed(
                        "User already exists", "Please check +help for available commands")
                    await ctx.channel.send(embed=embed)
                else:
                    payload = {
                        'login': 'student',
                        'uid': username,
                        'pwd': password,
                        'submit': 'Log Masuk'
                    }
                    if any(r.status_code == 302 for r in db.getResponse(payload).history):  # Successful login
                        db.addUser(discord_id, username, password)
                        embed = smallEmbed(
                            "User added!", "You can now use the bot's commands")
                        await ctx.channel.send(embed=embed)
                    else:  # Incorrect credentials
                        embed = smallEmbed(
                            "Incorrect credentials!", "Your login credentials don't match an account in our system")
                        await ctx.channel.send(embed=embed)
            except Exception:  # Error
                embed = exceptionEmbed()
                await ctx.channel.send(embed=embed)
        else:  # Invalid arguments
            embed = smallEmbed(
                "Invalid arguments", "Please check +help for available commands")
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel, discord.channel.DMChannel):  # Invalid channel
        await ctx.message.delete()
        embed = smallEmbed(
            "Invalid channel", "Please use this command in DMs")
        await ctx.channel.send(embed=embed)
        

@bot.command()
async def deluser(ctx):
    discord_id = ctx.author.id
    if (db.checkUser(discord_id)):
        try:  # Check if user exists
            db.deleteUser(discord_id)
            embed = smallEmbed(
                "User deleted!", "User has been succesfully deleted")
            await ctx.channel.send(embed=embed)
        except Exception:  # Error
            embed = exceptionEmbed()
            await ctx.channel.send(embed=embed)
    else:
        embed = smallEmbed(
            "User not found", "Please check +help for available commands")
        await ctx.channel.send(embed=embed)


@bot.command()
async def updatepass(ctx, *, args=None):
    discord_id = ctx.author.id
    if isinstance(ctx.channel, discord.channel.DMChannel) and ctx.author != bot.user:
        if args != None and len(args.split()) == 2:
            username, password = args.split()
            try:  # Check if user exists
                if (db.checkUser(discord_id)):
                    user = db.getUser(discord_id)
                    if (user['pwd'] == password):
                        embed = smallEmbed(
                            "Password unchanged!", "You have entered the same password!")
                        await ctx.channel.send(embed=embed)
                        return
                    else:
                        payload = {
                            'login': 'student',
                            'uid': username,
                            'pwd': password,
                            'submit': 'Log Masuk'
                        }
                        if any(r.status_code == 302 for r in db.getResponse(payload).history):  # Successful login
                            db.updatePass(discord_id, username, password)
                            embed = smallEmbed(
                                "Password Updated!", "Password has been updated successfully!")
                            await ctx.channel.send(embed=embed)
                        else:  # Incorrect credentials
                            embed = smallEmbed(
                                "Incorrect credentials!", "Your login credentials don't match an account in our system!")
                            await ctx.channel.send(embed=embed)
                else:   # User not found
                    embed = smallEmbed(
                        "User not found", "Please check +help for available commands")
                    await ctx.channel.send(embed=embed)
            except Exception:  # Error
                embed = exceptionEmbed()
                await ctx.channel.send(embed=embed)
        else:  # Invalid arguments
            embed = smallEmbed(
                "Invalid arguments", "Please check +help for available commands")
            await ctx.channel.send(embed=embed)
    elif not isinstance(ctx.channel, discord.channel.DMChannel):  # Invalid channel
        await ctx.message.delete()
        embed = smallEmbed(
            "Invalid channel", "Please use this command in DMs")
        await ctx.channel.send(embed=embed)
        

# check gpa
@bot.command()
async def gpa(ctx):
    discord_id = ctx.author.id
    if (db.checkUser(discord_id)):
        user = db.getUser(discord_id)
        try:
            if any(r.status_code == 302 for r in db.getResponse(user).history):  # Successful login
            
                wait_embed = smallEmbed("Please Wait", "GPA request is being processed...")
                wait_message = await ctx.channel.send(embed=wait_embed)
            
                # Perform the request
                r = db.getSession(user).get(GPA_URL)
                bs = BeautifulSoup(r.content, 'html.parser')
                gpa_element = bs.find_all(
                'td', text='Grade Points Average (GPA)')
            
                gpa_text = ""
            
                for i, gpa_element in enumerate(gpa_element, 1):
                    gpa_text += f"Semester {i}: {gpa_element.find_next_sibling().text}\n"
                
                embed = smallEmbed("Grade Points Average (GPA)", gpa_text)
            
                await wait_message.delete() # Delete the wait message
            
                await ctx.channel.send(embed=embed)
                
            else:
                
                embed = smallEmbed("Update Password!","!updatepass <username> <updated password>")
                await ctx.channel.send(embed=embed)
                return

        except Exception:
            embed = exceptionEmbed()
            await ctx.channel.send(embed=embed)
    else:
        embed = smallEmbed("Add user!","!adduser <username> <password>")
        await ctx.author.send(embed=embed)




bot.run(BOT_TOKEN)
