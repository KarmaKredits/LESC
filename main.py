import discord
from discord.ext import commands
import os

my_secret = os.environ['TOKEN']

##set up api grab from google sheets
team_db = {'LESC1':[
  {'name':'Pineapple On Pizza'	,'captain':'SassyBrenda' 	,'teammate':'KarmaKredits','division': 'US'},
  {'name':'Overconfident'	,'captain':'MrPriority'	,'teammate':'ChillCatDad','division': 'EU'},
  {'name':'The Ginger Brothers'	,'captain':'Noblent'	,'teammate':'ItsJeffTTV'		,'division': 'US'},
  {'name':'Up Your ARSEnal'	,'captain':'harm'	,'teammate':'yolomcshweg','division': 'EU'},
  {'name':'JustZees League' 	,'captain':'Shwa_Zee'	,'teammate':'justin.;p'		,'division': 'US'},
  {'name':'PERKELE'	,'captain':'Sant.'	,'teammate':'Normy','division': 'EU'},
  {'name':'Strawberries > Grapes'	,'captain':'Semper1515'	,'teammate':'SickLarry' 		,'division': 'US'},
  {'name':'LouisJames & His Cousin'	,'captain':'LouisJames'	,'teammate':'BigLez_THE_Bong_Head','division': 'EU'},
  {'name':'5'	,'captain':'Anubis' 	,'teammate':'Laggittarius'		,'division': 'US'},
  {'name':'AlphaKenny1'	,'captain':'DannyofthePaul'	,'teammate':'Azeria','division': 'EU'},
  {'name':'BobbyBuddy'	,'captain':'RuddyBuddy' 	,'teammate':'BobbyNay'		,'division': 'US'},
  {'name':'6'	,'captain':'Jamal751'	,'teammate':'Piers','division': 'EU'},
  {'name':'Big Cox'	,'captain':'Boxidize'	,'teammate':'Vl0xx' 		,'division': 'US'},
  {'name':'Fighting 13th'	,'captain':'Elephantagon' 	,'teammate':'MartPorsche','division': 'EU'},
  {'name':'Flying Avocados'	,'captain':'Avocado'	,'teammate':'FlyZK'		,'division': 'US'},
  {'name':'Gooch Slime'	,'captain':'Eddd_'	,'teammate':'jjjamie__','division': 'EU'},
  {'name':'Tiny Games'	,'captain':'Tiny' 	,'teammate':'CSmith_Games'		,'division': 'US'},
  {'name':'DNRB'	,'captain':'Rorymtb'	,'teammate':'Daughton','division': 'EU'},
  {'name':'Nked Dommer-nuts'	,'captain':'NK_XIV'	,'teammate':'Mdomm'		,'division': 'US'},
  {'name':'Failing 13th'	,'captain':'Benny_07' 	,'teammate':'Thomas','division': 'EU'},
  {'name':'Boost Over Ball'	,'captain':'TheDongerLord'	,'teammate':'VHP' 		,'division': 'US'},
  {'name':'O7'	,'captain':'HighSolution136'	,'teammate':'Ragdoll139','division': 'EU'},
  {'name':'Never Wallalols'	,'captain':'GingerSoccerMom'	,'teammate':'Midori'		,'division': 'US'},
  {'name':'I Need Boost'	'flyabl3' 	,'teammate':'holy nuggie','division': 'EU'},
  {'name':'The 2 Meatballs'	,'captain':'0val'	,'teammate':'Elekid123','division': 'EU'}
]}

participant_db = {}

client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  print('Bot Ready')
  # for team in team_db['LESC1']:
  #   print(team['division'])

  

@client.command()
async def ping(ctx):
  await ctx.send(f'Pong! {round(client.latency * 1000)} ms')

@client.command()
async def teams(ctx,season=1,division='all'):
  output = '**Teams:**\n'
  us = '__US Division:__'
  eu = '__EU Division:__'

  for team in team_db['LESC1']:
    if team['division']=='US':
      us = us + '\n' + team['name']
    elif team['division']=='EU':
      eu = eu + '\n' + team['name']
  if division == 'EU':
    output = output + eu
  elif division == 'US':
    output = output + us
  else:
    output = output + us + '\n\n'+ eu


  await ctx.send(output)

client.run(my_secret)