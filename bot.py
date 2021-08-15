import discord
from discord.ext import commands
import os
# from LESC import team_db
from LESC import participant_db
# from LESC import standingsUS
# from LESC import player_db
import re
from dotenv import load_dotenv
# from googleSheets import getDataFromGoogleSheets as getDB
import googleSheets

load_dotenv()
# TOKEN = os.getenv(key='TOKEN')
TOKEN = os.getenv(key='TOKEN_BETA', default=os.getenv('TOKEN'))

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  print('Bot Ready')
  await client.change_presence(activity=discord.Activity(name=".help",type=discord.ActivityType.watching))
  # get db info from googleSheets
  global LESC_DB
  LESC_DB = googleSheets.getDataFromGoogleSheets()
  global team_db
  team_db={}
  team_db['LESC1'] = googleSheets.formatRosters(LESC_DB)
  global standings_db
  standings_db = {}
  standings_db['LESC1'] = googleSheets.formatStandings(LESC_DB)
  playoffList=googleSheets.teamsInPlayoffs(LESC_DB)
  awardsTable = googleSheets.getAwards(LESC_DB)
  global player_db
  player_db = googleSheets.generateProfiles(team_db,playoffList,awardsTable)

@client.command(brief='Check bot latency')
async def ping(ctx):
  await ctx.send(f'Pong! {round(client.latency * 1000)} ms')

@client.command(brief='View the teams of a season')
async def season(ctx,*args):
  division = 'all' #default to all
  season = '1' #default to current
  for arg in args:
    if arg.lower() == 'eu':
      division = 'EU'
    elif arg.lower() == 'us':
      division = 'US'
    if arg == '1':
      season = '1'

  us = ''
  eu = ''

  embedTitle='LESC Season ' + season + ' Teams'
  embedVar = discord.Embed(title=embedTitle, color=0xffffff)

  for team in team_db['LESC'+season]:
    if team['division'].upper()=='US':
      us = us + '\n' + team['team']
    elif team['division'].upper()=='EU':
      eu = eu + '\n' + team['team']

  if division in ['US','all']:
    embedVar.add_field(name="US Division", value=us, inline=True)

  if division in ['EU','all']:
    embedVar.add_field(name="EU Division", value=eu, inline=True)

  await ctx.send(embed=embedVar)

@client.command(brief='View team rosters')
async def teams(ctx,*args):
    global team_db
    division = [] #default to all
    season = '1' #default to current
    for arg in args:
        if arg.lower() == 'eu':
            division.append('EU')
        elif arg.lower() == 'us':
            division.append('US')
        elif arg == '1':
            season = '1'
    if len(division)<1:
        division = ['US','EU']

    embedTitle='LESC Season ' + season + ' Teams'

    for div in division:
        embedVar = discord.Embed(title=embedTitle,description='**' + div + ' Division**', color=0xffffff)
        for col in ['team','captain','teammate']:
            val = []
            for team in team_db['LESC'+season]:
                if team['division'] == div:
                    val.append(team[col])
            embedVar.add_field(name=col.capitalize(), value='\n'.join(val), inline=True)
        await ctx.send(embed=embedVar)
        embedVar.clear_fields



@client.command(brief='View season standings')
async def standings(ctx,*args):
    global standings_db
    division = [] #default to all
    season = '1' #default to current
    for arg in args:
        if arg.lower() == 'eu':
            division.append('EU')
        elif arg.lower() == 'us':
            division.append('US')
        elif arg == '1':
            season = '1'
    if len(division)<1:
        division = ['US','EU']


    for div in division:
        matches = standings_db['LESC'+season][div]
        title = '**LESC Season ' + season + ' - '+ div +' Standings**\n'
        string = ''
        temp = ''
        coln=len(matches[0])-1
        # print('coln: ' + str(coln))
        rown=len(matches)-1
        # print('rown: ' + str(rown))
        maxchar = []
        for col in range(coln):
            maxn=0
            for row in matches:
                # print(row[col])
                if len(row[col]) > maxn:
                    maxn=len(row[col])
                    # print(row[col] + ' - ' + str(len(row[col])))
            maxchar.append(maxn)
        # print(maxchar)
        rowlist = []
        for line in matches:
            rowtext = ''
            font=''
            # if line[0].isnumeric():
            #     if int(line[0])>7:
            #         font='- '
            #     else:
            #         font='+ '
            # print(line)
            for col in range(coln):
                # print(line[col])
                diff = maxchar[col]-len(line[col]) + 2
                rowtext = rowtext + line[col] + (' '*diff)
            rowlist.append(font+rowtext)
        string = '\n'.join(rowlist)
        await ctx.send(title + "```" + string + "```")

@client.command(description='view the LESC profile of yourself or the mentioned user',brief='View LESC profile of [user], defaults to self')
async def profile(ctx, arg = None):
    if arg == None:
        arg = ctx.author.display_name #mention
    not_found = True
    global player_db
    for playerkey in player_db:
        pp=player_db[playerkey]
        if arg.lower() == playerkey.lower() or arg.lower() in playerkey.lower():
            embedVar = discord.Embed(title=pp['player'], description='The League of Extraordinary Soccer Cars', color=0xffffff)
            embedVar.add_field(name='Seasons',value='\n'.join(pp['season']),inline=True)
            embedVar.add_field(name='Teams',value='\n'.join(pp['teams']),inline=True)
            embedVar.add_field(name='Teammates',value='\n'.join(pp['teammates']),inline=True)
            embedVar.add_field(name='Awards',value='\n'.join(pp['awards']),inline=True)
            await ctx.send(embed=embedVar)
            embedVar.clear_fields
            not_found = False
    if not_found:
        await ctx.send('Profile not found')

# @client.command()
# async def prefix(ctx, arg = '.'):
#   global client
#   client = commands.Bot(command_prefix = arg)
#   await ctx.send('Command prefix changed to "' + arg +'"')

@client.command(brief='Link to invite this bot your own server')
async def invite(ctx):
    string = f'Click the link below to invite {client.user.name} to your server \n'
    link = 'https://discord.com/api/oauth2/authorize?client_id=873361977991381043&permissions=223296&scope=bot'
    await ctx.send(string+link)

@client.command(aliases=['doc','data','stats'],brief='Link to LESC Google Sheet')
async def sheet(ctx):
    string= 'Click the link below to go to the offical LESC spreadsheet\n'
    link='https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777'
    await ctx.send(string+link)

@client.command(brief='Link to invite this bot your own server')
async def feedback(ctx):
    string = f'Click the link below to give feedback on the LESC \n'
    link = 'https://discord.com/api/oauth2/authorize?client_id=873361977991381043&permissions=223296&scope=bot'
    block = """**LESC Season 2 is COMING SOON ™️ to a discord server near you!**

We want to give you the best Season 2 that we can, and for that we need your help! We've compiled a survey that will help us find out what you want from the LESC, so that we can tweak the format of the competition and make it more fun for everyone. Please head to https://forms.gle/3VfB5nNuwakzSU178 to share your thoughts and opinions.

This survey is for **EVERYONE**, it doesn't matter if you are a **Substitute**, **Commentator**, or **Viewer**, we want your feedback and ideas!

**Two things to note:**
Firstly, please be honest! We can't improve if we don't know how you lot feel.
Secondly, we wont share any answers/information your provide outside of the commissioners, and your email addresses are not recorded by us."""
    await ctx.send(block)

client.run(TOKEN)
