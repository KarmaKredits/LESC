import discord
from discord.ext import commands
import os
# from LESC import team_db
# from LESC import participant_db
# from LESC import standingsUS
# from LESC import player_db
import re
from dotenv import load_dotenv
# from googleSheets import getDataFromGoogleSheets as getDB
import googleSheets
from redisDB import redisDB
from datetime import datetime
from datetime import timedelta
import time as t
twitchTracking = {}
import twitchWatcher as tw
import asyncio
import math

load_dotenv()
# TOKEN = os.getenv(key='TOKEN')
TOKEN = os.getenv(key='TOKEN_BETA', default=os.getenv('TOKEN'))

intents = discord.Intents.default()
intents.members = True
bot = discord.Client(intents=intents)
client = commands.Bot(command_prefix = '.')
lescTitle='The League of Extraordinary Soccer Cars'
testGuild=183763588870176768
logChannel=866129852708814858
log = None
last_sorted_list = []

def updateFromGoogleSheets():
    try:
        # get db info from googleSheets
        print('loading data from google sheets...')
        global LESC_DB
        LESC_DB = googleSheets.getDataFromGoogleSheets()
        rc.setValue(key='lesc_db',value=LESC_DB)

    except Exception as e:
        msg =  log.send(e)
        newcontent = 'Google Sheet Update:\n' + msg.content
        msg.edit(content=newcontent)
        raise


@client.event
async def on_ready():
    print('LOADING...')
    await client.change_presence(activity=discord.Activity(name=".help",type=discord.ActivityType.watching))

    step = 'log'

    global log
    log = client.get_channel(logChannel)

    global rc
    rc=redisDB()

    try:
        # get db info from googleSheets
        print('loading data from google sheets...')
        step = 'redis DB'
        global LESC_DB
        # LESC_DB = googleSheets.getDataFromGoogleSheets()
        # rc.setValue(key='lesc_db',value=LESC_DB)
        LESC1_DB = rc.getValue('lesc_db') #LESC1


        print('formating rosters...')
        step = 'rosters'
        global team_db
        team_db={}
        team_db['LESC1'] = googleSheets.formatRosters(LESC1_DB)
        # rc.setValue(key='rosters',value=team_db)

        print('formating standings...')
        step = 'standings'
        global standings_db
        standings_db = {}
        standings_db['LESC1'] = googleSheets.formatStandings(LESC1_DB)
        # rc.setValue(key='standings',value=standings_db)
        playoffList=googleSheets.teamsInPlayoffs(LESC1_DB)
        awardsTable = googleSheets.getAwards(LESC1_DB)

        print('generating profiles...')
        step = 'profiles'
        global player_db
        player_db = googleSheets.generateProfiles(team_db,playoffList,awardsTable)

        print('loading participants from redis...')
        step = 'redis participants'
        global participant_db
        participant_db = rc.getValue('participants')
        # print(participant_db)
        # print(participant_db['sassybrenda'])
        # print(participant_db['karmakredits'])
        for player in participant_db:
            # print(player)
            if not ('id' in participant_db[player]):
                print('id not found')
                participant_db[player]['id']=0
            if not('quote' in participant_db[player]):
                print('quote found')
                participant_db[player]['quote']=''

        print('formating matches...')
        step = 'matches'
        global matches_db
        matches_db = {}
        matches_db['LESC1'] = googleSheets.getMatches(LESC1_DB)

        # get guild
        # print(client.guilds[0].name)
        guildLESC = client.get_guild(183763588870176768)
        # print(guildLESC)

        step = 'keys'
        rc.printKeys()

    except Exception as e:
        msg = await log.send(e)
        newcontent = step + ':\n' + msg.content
        await msg.edit(content=newcontent)
        raise

    print('Bot Ready')
    print('==========================')
    # twitchAlerts()
    print('execute cycle from ready')
    task1 = asyncio.create_task(cycle(10))



# def logErr(arg):
#     await log.send(arg)

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
        print(arg)
    elif len(arg)<3:
        await ctx.message.reply('Please use at least 3 characters for profile name search')
        return
    not_found = True
    global participant_db

    for playerkey in participant_db:
        # print(playerkey)
        pp=participant_db[playerkey]
        if (arg.lower() == playerkey.lower()) or (arg.lower() in playerkey.lower() and len(arg)>2):
            description = ''
            if len(pp['quote'])>1:
                description = '*"'+ pp['quote'] +'"*'
            embedVar = discord.Embed(title=pp['player'], description=description, color=0xffffff)
            embedVar.add_field(name='Seasons',value='\n'.join(pp['season']),inline=True)
            embedVar.add_field(name='Teams',value='\n'.join(pp['teams']),inline=True)
            embedVar.add_field(name='Teammates',value='\n'.join(pp['teammates']),inline=True)
            embedVar.add_field(name='Awards',value='\n'.join(pp['awards']),inline=True)
            embedVar.set_footer(text=lescTitle,icon_url='https://cdn.discordapp.com/icons/835907044024123473/3963713137e01ae8b9c0be2311dc434c.png')
            await ctx.send(embed=embedVar)
            embedVar.clear_fields
            not_found = False
    season_sub= ['860144876866502666', # S1 US Sub
    '860145226224107550',# S1 EU Sub
    '843196839057948722'] #test
    award_sub=['869417365975224340', # S1 Participant
    '695490219687804928'] #test
    if not_found:
        if arg.lower()==ctx.author.display_name.lower():
            season_list = ['-']
            award_list = ['-']
            for role in ctx.author.roles:
                if str(role.id) in season_sub:
                    print('season')
                    print(role.name)
                    season_list.insert(0,role.name)
                if str(role.id) in award_sub:
                    print('award')
                    print(role.name)
                    award_list.insert(0,role.name)
            if len(season_list) or len(award_list):
                key=arg.lower()
                participant_db[key] = {'player':arg,
                    'season':season_list,'teams':['-'],'teammates':['-'],'awards':award_list,'id':0,'quote':''}
                if len(participant_db[key]['season'])>1 and '-' in participant_db[key]['season']: participant_db[key]['season'].remove('-')
                if len(participant_db[key]['awards'])>1 and '-' in participant_db[key]['awards']: participant_db[key]['awards'].remove('-')
                embedVar = discord.Embed(title=arg, color=0xffffff)
                embedVar.add_field(name='Seasons',value='\n'.join(participant_db[key]['season']),inline=True)
                embedVar.add_field(name='Teams',value='\n'.join(participant_db[key]['teams']),inline=True)
                embedVar.add_field(name='Teammates',value='\n'.join(participant_db[key]['teammates']),inline=True)
                embedVar.add_field(name='Awards',value='\n'.join(participant_db[key]['awards']),inline=True)
                embedVar.set_footer(text=lescTitle)
                await ctx.send(embed=embedVar)
                try:
                    rc.setValue('participants',participant_db) #save user to db
                except Exception as e:
                    msg = await log.send(e)
                    newcontent = 'save user to redis participants: '+ arg + '\n' + msg.content
                    await msg.edit(content=newcontent)
                    raise

            else:
                ctx.send('No season roles')
        else:
            await ctx.message.reply('Profile not found')

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

@client.command(aliases=['doc','data','stats','sheets'],brief='Link to LESC Google Sheet')
async def sheet(ctx):
    string= 'Click the link below to go to the offical LESC spreadsheet\n'
    link='https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777'
    await ctx.send(string+link)

@client.command(brief="!Link to the LESC feedback form!")
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

@client.command(brief="Link LESC profile to your discord")
async def claim(ctx, arg=None):
    print('claim command used')
    to_send = ''
    if arg == None:
        print('no arg')
        arg = ctx.author.display_name
        to_send = 'No name given, using Discord display name: ' + str(ctx.author.display_name) + '\n'
    arg = arg.lower()
    if arg in participant_db:
        print('arg found')
        participant_db[arg]['id']=ctx.author.id
        link_text = '<@' + str(ctx.author.id) + '> linked with ' + participant_db[arg]['player']
        to_send = to_send + 'Profile name found! ' + link_text
        try:
            rc.setValue('participants',participant_db)
            await log.send(link_text)
        except Exception as e:
            msg = await log.send(e)
            newcontent = 'claim redis participants: '+ arg + '\n' + msg.content
            await msg.edit(content=newcontent)
            raise

    else:
        print(arg + ' not found')
        to_send = to_send + arg + ' not found'
    await ctx.message.reply(to_send)
#
@client.command(brief="Add self quote to your profile")
async def quote(ctx, *args):
    response = ''
    if len(args) == 0:
        print('None')
        response = 'No quote detected. use this format:\n.quote "your quote here, enclosed by double-quotation marks"'
    elif len(args)>0:
        found=False
        for player in participant_db:
            if participant_db[player]['id'] == ctx.author.id:
                print('found claimed profile')
                found = True
                if len(args)>1:
                    quote = ' '.join(args)
                else:
                    quote = args[0]

                participant_db[player]['quote'] = quote
                try:
                    rc.setValue('participants',participant_db)
                    response = 'Profile quote set to:\n*"' + quote + '"*'
                    await log.send('<@' + str(ctx.author.id) + '> has set ' + player + ' quote to: ' + quote)
                except Exception as e:
                    msg = await log.send(e)
                    newcontent = 'quote to redis participants: '+ arg + '\n' + msg.content
                    await msg.edit(content=newcontent)
                    raise
        if not found:
            response = 'You must first claim your profile, please use the ".claim <profile name>" command to claim your profile'
    if len(response)>1:
        await ctx.message.reply(response)

@client.command(brief="Search matches of team")
async def matches(ctx, arg = ''):
    global matches_db
    if arg == '':
        await ctx.message.reply('Please include part of team name you wish to lookup. For example,**.matches never**, to look up matches for the "Never Wallalols"')
        return
    searchTerm = arg
    prepList = []
    max = {
        'home': 0,
        'away': 0,
        'day': 0,
        'date': 0,
        'time': 0,
        # 'commentators': 0,
        'result': 0
        }
    header = {
        'home': 'Home Team',
        'away': 'Away Team',
        'day': 'Day',
        'date': 'Date',
        'time': 'Time',
        # 'commentators': 0,
        'result': 'Result'
        }
    for div in matches_db['LESC1']:

        for match in matches_db['LESC1'][div]:
            if searchTerm.lower() in match['home'].lower() or searchTerm.lower() in match['away'].lower():
                for m in max:
                    if max[m] < len(match[m]):
                        max[m] = len(match[m])
                prepList.append(match)
    head = []
    for key in max:
        head.append(header[key] + ' '*(max[key]-len(header[key])))
    output = 'LESC Season 1\n' + '  '.join(head)
    for match in prepList:
        output = output + "\n"
        temp = []
        for key in max:
            temp.append(match[key] + ' '*(max[key]-len(match[key])))
        output = output + '  '.join(temp)
    # print(output)
    await ctx.send('```' + output + '```')

# @client.command(brief="Return streams online")
# async def on(ctx, arg = ''):
#     tw.getToken()
#     embed = discord.Embed(title='Steamers Online', color=0xffffff)
#     for streamer in tw.streamerlist:
#         stream = tw.getStreamsFromLogin(streamer)
#         print(stream)
#         if len(stream) > 0:
#             user_name = stream[0]['user_name']
#             game_name = stream[0]['game_name']
#             title = stream[0]['title']
#             login = stream[0]['user_login']
#             embed.add_field(name=user_name, value=game_name + '\n[' + title + '](https://www.twitch.tv/' + login +')',inline=False)
#     await ctx.send(embed=embed)

@client.command(brief="Return streamers online or next schedule stream")
async def streams(ctx, arg = ''):
    msg = await ctx.send('Fetching dem streamers...')
    tw.getToken()
    user_list = tw.getUserIDFromLogin('&login='.join(tw.streamerlist))
    embed = discord.Embed(title='LESC Community Streams', color=0xffffff)
    embed.set_footer(text = 'DM KarmaKredits to be added to streamer list')
    now = datetime.utcnow()
    list = []
    for user in user_list:
        # print(user['id'], '\n')
        sched = tw.getScheduleFromUserID(user['id'])
        if sched == None: sched = []
        # print(sched)
        # print(user['display_name'])
        stream = tw.getStreamsFromLogin(user['login'])
        if stream == None: stream = []
        # print(stream)
        if len(stream) > 0:
            user_name = stream[0]['user_name']
            game_name = stream[0]['game_name']
            title = stream[0]['title']
            login = stream[0]['user_login']
            dt_start = datetime.strptime(stream[0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')
            list.append({'time' : dt_start, 'data' : {'name':user_name, 'value':'[' + title + '](https://www.twitch.tv/' + login +')\n'+game_name}})
        elif len(sched)>0:
            start_time = sched[0]['start_time']
            dt_start = datetime.strptime(sched[0]['start_time'], '%Y-%m-%dT%H:%M:%SZ')
            delta = dt_start - now
            if delta.total_seconds() > -300:
                login_name = user['login']
                display_name = user['display_name']
                title = sched[0]['title']
                game = 'Not Specified'
                if sched[0]['category'] != None: game = sched[0]['category']['name']
                # print(delta)
                # await ctx.send(delta)
                delta = delta - timedelta(microseconds=delta.microseconds)
                hours = delta.total_seconds()/3600
                list.append({'time' : dt_start, 'data' : { 'name' : display_name, 'value' : title + '\nGame: ' + game + '\n Starting in T-' + str(delta)}})
    #sort list
    sorted_list = []
    # for spot in range(len(list)):
    # print(list)
    while len(list)>0:
        earliest = None
        keytopop = 0
        for key in range(len(list)):
            # print(earliest, list[key]['time'])
            if earliest == None:
                earliest = list[key]['time']
                keytopop = key
            elif earliest > list[key]['time']:
                earliest = list[key]['time']
                keytopop = key
        # print(list[key])
        sorted_list.append(list.pop(keytopop))
    # print(sorted_list)
    # add to fields
    for item in sorted_list:
        embed.add_field(name = item['data']['name'], value = item['data']['value'], inline = True)
        # embed.add_field(name = '\u200b', value = '\u200b', inline = False)
    # await ctx.send(embed=embed)
    await msg.edit(content = '', embed=embed)


async def twitchAlerts():
    global last_sorted_list
    print('twitchAlert check')
    tw.getToken()
    user_list = tw.getUserIDFromLogin('&login='.join(tw.streamerlist))
    embed = discord.Embed(title='LESC Community Streams', color=0xffffff)
    embed.set_footer(text = 'DM KarmaKredits to be added to streamer list')
    now = datetime.utcnow()
    list = []
    next_time = None
    for user in user_list:
        sched = tw.getScheduleFromUserID(user['id'])
        if sched == None: sched = []
        stream = tw.getStreamsFromLogin(user['login'])
        if stream == None: stream = []
        if len(stream) > 0:
            user_name = stream[0]['user_name']
            game_name = stream[0]['game_name']
            title = stream[0]['title']
            login = stream[0]['user_login']
            dt_start = datetime.strptime(stream[0]['started_at'], '%Y-%m-%dT%H:%M:%SZ')
            list.append({'time' : dt_start, 'data' : {'name':user_name, 'value':'[' + title + '](https://www.twitch.tv/' + login +')\n'+game_name}})
        elif len(sched)>0:
            start_time = sched[0]['start_time']
            dt_start = datetime.strptime(sched[0]['start_time'], '%Y-%m-%dT%H:%M:%SZ')
            delta = dt_start - now
            delta = delta - timedelta(microseconds=delta.microseconds)
            if delta.total_seconds()<-300:
                None
                print('less than 300')
            else:
                login_name = user['login']
                display_name = user['display_name']
                title = sched[0]['title']
                game = 'Not Specified'
                if sched[0]['category'] != None: game = sched[0]['category']['name']
                hours = delta.total_seconds()/3600
                secs_til = math.floor(delta.total_seconds())
                if next_time == None: next_time = secs_til
                elif secs_til < next_time: next_time = secs_til
                list.append({'time' : dt_start, 'data' : { 'name' : display_name, 'value' : title + '\nGame: ' + game + '\n Starting in T-' + str(delta)}})
    #sort list
    sorted_list = []
    # for spot in range(len(list)):
    while len(list)>0:
        earliest = None
        keytopop = 0
        for key in range(len(list)):
            if earliest == None:
                earliest = list[key]['time']
                keytopop = key
            elif earliest > list[key]['time']:
                earliest = list[key]['time']
                keytopop = key
        sorted_list.append(list.pop(keytopop))
    # add to fields
    sorted_list_check = []
    for item in sorted_list:
        embed.add_field(name = item['data']['name'], value = item['data']['value'], inline = True)
        sorted_list_check.append(item['data']['name'])

    # print('done')
    # print('pre',next_time)
    if next_time == None: next_time = 12*60*60
    else: next_time = math.floor(next_time/2)
    # print('post',next_time)
    if (next_time <60 and next_time >= 0) or (sorted_list_check != last_sorted_list and last_sorted_list != []):
        print('next_time <60 and next_time > 0', next_time)
        print('sorted_list != last_sorted_list and last_sorted_list != []',sorted_list_check, last_sorted_list)
        await log.send(embed=embed)

    last_sorted_list = sorted_list_check

    return next_time

async def cycle(seconds):
    # print('cycle start', 'execute twitch Alerts')
    wait_time = await twitchAlerts()
    # await wait_time
    # print('wait_time', wait_time)

    if wait_time < 60: wait_time = 60
    print('sleep',wait_time)
    await asyncio.sleep(wait_time)
    # print('wake,''execute cycle')
    # asyncio.create_task(cycle(wait_time))
    # print('cycle end', seconds)
    return asyncio.create_task(cycle(wait_time))

if __name__ == '__main__':
    client.run(TOKEN)
