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
TOKEN = os.getenv(key='TOKEN')
my_secret = os.environ['TOKEN']
LESC1url = 'https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit?usp=sharing'
LESC1test = 'https://docs.google.com/spreadsheets/d/1DGpfnwq57um8KmXQEGIqby3nUqfK7Q4SbvXOfsbZsdM/edit?usp=sharing'
testID = '1DGpfnwq57um8KmXQEGIqby3nUqfK7Q4SbvXOfsbZsdM'






##US TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=A2:C15

##EU TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=E2:G16


client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  print('Bot Ready')
  await client.change_presence(activity=discord.Activity(name=".help",type=discord.ActivityType.watching))
  # for team in team_db['LESC1']:
  #   print(team['name'])
  global LESC_DB
  LESC_DB = googleSheets.getDataFromGoogleSheets()
  global team_db
  team_db={}
  team_db['LESC1'] = googleSheets.formatRosters(LESC_DB)
  global standings_db
  standings_db = {}
  standings_db['LESC1'] = googleSheets.formatStandings(LESC_DB)
  global player_db
  player_db = googleSheets.generateProfiles(team_db)

@client.command()
async def ping(ctx):
  await ctx.send(f'Pong! {round(client.latency * 1000)} ms')

@client.command()
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
      us = us + '\n' + team['name']
    elif team['division'].upper()=='EU':
      eu = eu + '\n' + team['name']

  if division in ['US','all']:
    embedVar.add_field(name="US Division", value=us, inline=True)

  if division in ['EU','all']:
    embedVar.add_field(name="EU Division", value=eu, inline=True)

  await ctx.send(embed=embedVar)

@client.command()
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
        for col in ['name','captain','teammate']:
            val = []
            print(col)
            for team in team_db['LESC'+season]:
                if team['division'] == div:
                    val.append(team[col])
        embedVar.add_field(name=col.capitalize(), value='\n'.join(val), inline=True)
        await ctx.send(embed=embedVar)
        embedVar.clear_fields



@client.command()
async def standings(ctx,*args):
    global standings_db
    division = [] #default to all
    season = '1' #default to current
    for arg in args:
        print(arg)
        if arg.lower() == 'eu':
            division.append('EU')
        elif arg.lower() == 'us':
            division.append('US')
        elif arg == '1':
            season = '1'
    if len(division)<1:
        division = ['US','EU']


    for div in division:
        matches = standings_db[div]
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

@client.command(description='view the LESC profile of yourself or the mentioned user',brief='LESC profile of [user] or default to self')
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


client.run(my_secret)
