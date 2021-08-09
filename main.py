import discord
from discord.ext import commands
import os
from LESC import team_db

my_secret = os.environ['TOKEN']

##US TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=A2:C15

##EU TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=E2:G16



participant_db = {}

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  print('Bot Ready')
  for team in team_db['LESC1']:
    print(team['name'])

  

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
  division = [] #default to all
  season = '1' #default to current
  for arg in args:
    if arg.lower() == 'eu':
      division = division.append('EU')
    elif arg.lower() == 'us':
      division = division.append('US')
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

client.run(my_secret)