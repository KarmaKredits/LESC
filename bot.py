import discord
from discord.ext import commands
import os
# from LESC import team_db
from LESC import participant_db
# from LESC import standingsUS
from LESC import player_db
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



# range_names = [
#     # Range names ...
# ]
# result = service.spreadsheets().values().batchGet(
#     spreadsheetId=spreadsheet_id, ranges=range_names).execute()
# ranges = result.get('valueRanges', [])
# print('{0} ranges retrieved.'.format(len(ranges)))

# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options

# chrome_options = Options()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--disable-dev-shm-usage')

# driver = webdriver.Chrome(options=chrome_options)
# driver.get("https://youtube.com")

# regex = '(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)\t(.+)'
# p = re.compile(regex)
# # print(standingsUS)
# matches = p.findall(standingsUS)
# standingsUS_db = {}
#
# standingsUS_db['header'] = matches[0]
# standingsUS_db['rows'] = []
# standingsUS_db['data'] = [[]]
# for row in range(len(matches)-1):
#   # print(matches[row+1])
#   standingsUS_db['rows'].append(matches[row+1])
#   # for col in range(len(matches[row+1])):
#   #   standingsUS_db['data'][col] = []
#   #   standingsUS_db['data'][col][row] = matches[row+1][col]
#   # print(len(item))
#   # print(type(item))
#   # for i in item:
#     # print(i)
# # print(standingsUS)



##US TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=A2:C15

##EU TEAM Link
# https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777&range=E2:G16


client = commands.Bot(command_prefix = '.')

@client.event
async def on_ready():
  print('Bot Ready')
  # for team in team_db['LESC1']:
  #   print(team['name'])
  global LESC_DB
  LESC_DB = googleSheets.getDataFromGoogleSheets()
  global team_db
  team_db = googleSheets.formatRosters(LESC_DB)
  global standings_db
  standings_db = googleSheets.formatStandings(LESC_DB)

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
  # print (ctx.author.mention)
  # print (arg)
  # embedVar = discord.Embed(title=arg, color=0xffffff)
  not_found = True
  for player in player_db:
    if arg.lower() == player['player'].lower() or arg.lower() in player['player'].lower():
      embedVar = discord.Embed(title=player['player'], description='The League of Extraordinary Soccer Cars', color=0xffffff)
      embedVar.add_field(name='Seasons',value='\n'.join(player['season']),inline=True)
      embedVar.add_field(name='Teams',value='\n'.join(player['teams']),inline=True)
      embedVar.add_field(name='Teammates',value='\n'.join(player['teammates']),inline=True)
      embedVar.add_field(name='Awards',value='\n'.join(player['awards']),inline=True)
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
