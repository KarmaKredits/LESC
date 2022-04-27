import discord
from discord.ext import commands
import os
import re
from dotenv import load_dotenv
# from googleSheets import getDataFromGoogleSheets as getDB
import googleSheets
import LESC3
from redisDB import redisDB
import calendar
from datetime import datetime, timedelta
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
intents.messages = True
# print('intents: ',intents)
# bot = discord.Client(intents=intents)
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
client = commands.Bot(command_prefix = '.', help_command=help_command,intents=intents)
# client.intents = intents
# client.Intents.members = True
lescTitle='The League of Extraordinary Soccer Cars'
testGuild=183763588870176768
guildTESTID = 183763588870176768
guildLESCID = 835907044024123473
logChannel=866129852708814858
lescLiveChannelID = 890650216909406288
log = None
lescLiveChannel = None
last_sorted_list = []
last_live = []

async def updateFromGoogleSheets():
    response = ''
    try:
        # get db info from googleSheets
        print('loading data from google sheets...')
        divisions = [1,2,3,4]
        divisionNames = ['NA Upper','NA Lower','EU Upper', 'EU Lower']
        divisionKey = ['naupper','nalower','euupper', 'eulower']
        global LESC3_DB
        LESC3_DB = googleSheets.getDataFromGoogleSheets() #current season only
        #sync existing and new data
        # print('LESC3_DB',LESC3_DB)

        if LESC3_DB is not None:
            # rc1 = redisDB()
            response = 'Unable to update Redis, contact KarmaKredits'
            rc.setValue(key='lesc3_db',value=LESC3_DB) # overwrite
            response = 'Update Successful'
        else:
            response = 'Unable to connect to Google Sheets, contact KarmaKredits'

    except Exception as e:
        response = 'Unable to connect to sheets, contact KarmaKredits'
        # msg =  log.send(e)
        # newcontent = 'Google Sheet Update:\n' + msg.content
        # msg.edit(content=newcontent)
        print(e)
        raise
    return response

def variable_update():
    global team_db
    team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)
    global standings_db
    standings_db['LESC3'] = LESC3.formatStandings(LESC3_DB)
    global matches_db
    matches_db['LESC3'] = LESC3.getMatches(LESC3_DB)

@client.event
async def on_ready():
    print('LOADING...')
    await client.change_presence(activity=discord.Activity(name=".help",type=discord.ActivityType.watching))

    step = 'log'

    global log
    log = client.get_channel(logChannel)

    step = 'lescLiveChannel'
    try:
        global lescLiveChannel
        lescLiveChannel = client.get_channel(lescLiveChannelID)
        # print('?????????????????????')
    except:
        pass

    global rc
    rc=redisDB()

    global LESC3_DB
    try:
        step = 'updateFromGoogleSheets'
        response = await updateFromGoogleSheets() #temp
    except Exception as e:
        print('db from redis')
        # LESC3_DB = rc.getValue('lesc3_db') #LESC1
        msg = await log.send(e)
        newcontent = step + ':\n' + msg.content
        await msg.edit(content=newcontent)
        # pass

    try:
        # get db info from googleSheets
        print('loading data from google sheets...')
        step = 'redis DB'
        # global LESC_DB
        # LESC2_DB = googleSheets.getDataFromGoogleSheets()
        # rc.setValue(key='lesc2_db',value=LESC2_DB)

        LESC1_DB = rc.getValue('lesc_db') #LESC1
        LESC2_DB = rc.getValue('lesc2_db') #LESC2
        LESC3_DB = rc.getValue('lesc3_db')

        print('formating rosters...')
        step = 'rosters'
        global team_db
        team_db={}
        team_db['LESC1'] = googleSheets.formatRosters(LESC1_DB)
        team_db['LESC2'] = googleSheets.formatRosters(LESC2_DB)
        team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)
        # rc.setValue(key='rosters',value=team_db)

        print('formating standings...')
        step = 'standings'
        global standings_db
        standings_db = {}
        standings_db['LESC1'] = googleSheets.formatStandings(LESC1_DB)
        standings_db['LESC2'] = googleSheets.formatStandings(LESC2_DB)
        standings_db['LESC3'] = LESC3.formatStandings(LESC3_DB)
        # rc.setValue(key='standings',value=standings_db)
        print('playoffs')
        playoffList = {}
        playoffList['LESC1'] = googleSheets.teamsInPlayoffs(LESC1_DB)
        playoffList['LESC2'] = googleSheets.teamsInPlayoffs(LESC2_DB)
        playoffList['LESC3'] = []

        print('awards')
        awardsTable = {}
        awardsTable['LESC1']  = googleSheets.getAwards(LESC1_DB)
        # awardsTable['LESC2']  = []
        awardsTable['LESC2']  = googleSheets.getAwards(LESC2_DB)
        awardsTable['LESC3'] = []
        print('generating profiles...')
        step = 'profiles'
        global player_db
        player_db = googleSheets.generateProfiles(team_db,playoffList,awardsTable)
        # print(player_db)
        print('loading participants from redis...')
        step = 'redis participants'
        global participant_db
        participant_db = rc.getValue('participants')

        for player in player_db:
            # print(player)
            if player not in participant_db:
                # print('new')
                participant_db[player] = player_db[player]
                participant_db[player]['id']=0
                participant_db[player]['quote']=''
            else:
                for season in player_db[player]['season']:
                    if not (season in participant_db[player]['season']):
                        # print('season not: ', season)
                        participant_db[player]['season'].append(season)
                for team in player_db[player]['teams']:
                    if not (team in participant_db[player]['teams']):
                        # print('team not: ', team)
                        participant_db[player]['teams'].append(team)
                for teammate in player_db[player]['teammates']:
                    if not (teammate in participant_db[player]['teammates']):
                        # print('teammate not: ', teammate)
                        participant_db[player]['teammates'].append(teammate)
                for award in player_db[player]['awards']:
                    if not (award in participant_db[player]['awards']):
                        # print('award not: ', award)
                        participant_db[player]['awards'].append(award)
        # print('test')
        for player in participant_db:
            # print(player)
            for item in participant_db[player]:
                # print(item)
                if item in ['season', 'teams', 'teammates', 'awards']:
                    # print(item)
                    if len(participant_db[player][item]) > 1 and ('-' in participant_db[player][item]):
                        try:
                            participant_db[player][item].remove('-')
                        except Exception as e:
                            print('Removal of "-" in participant_db:\n', e)
                            pass

        # print(participant_db)
        # print(participant_db['sassybrenda'])
        # print(participant_db['karmakredits'])

        print('formating matches...')
        step = 'matches'
        global matches_db
        matches_db = {}
        matches_db['LESC1'] = googleSheets.getMatches(LESC1_DB)
        matches_db['LESC2'] = googleSheets.getMatches(LESC2_DB)
        matches_db['LESC3'] = LESC3.getMatches(LESC3_DB)
        # schedule = checkForMatches() #test


        # get guild
        # print(client.guilds[0].name)
        global guildLESC
        guildLESC = None
        try:
            guildLESC = client.get_guild(guildLESCID)
        except: pass
        print('+++++++++++++++++++++++')
        print(guildLESC)

        # for item in guildLESC.members:
        #     print(item)

        global guildTEST

        guildTEST = client.get_guild(guildTESTID)
        print(guildTEST)
        # print(client.get_guild(183763588870176768))
        me = await guildTEST.fetch_member(174714475113480192)
        print(me)
        # await log.send(me.mention)
        # members = await guildTEST.fetch_members(limit=150).flatten()
        # print(members)
        for item in guildTEST.members:
            print(item)

        step = 'keys'
        rc.printKeys()
        print(int(t.time()))

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

@client.command(brief='Update DB from Google Sheets (Commissioners ONLY)')
async def update(ctx):
    roles = [183800165767970820, #life guard
    835907130074333184] #commissioners
    userOverride = [174714475113480192] #karmakredits id
    # print(ctx.author.roles)
    allowed = False
    #check for KarmaKredits
    if ctx.author.id in userOverride:
        allowed = True
        # print('userOverride')
        #check roles
    for roleNeeded in roles:
        # print(roleNeeded)
        if allowed: break
        for role in ctx.author.roles:
            if role.id == roleNeeded:
                allowed = True
                # print('found')
                break
    # print(allowed)
    if allowed:
        print('update executed')
        msg = await ctx.reply('Updating DB from Sheets...')
        response = await updateFromGoogleSheets()
        if response == 'Update Successful':
            variable_update()
            print('variable update')
        await msg.edit(content=response)


@client.command(brief='List available subs',
    aliases=['subs','substitute','substitutes'])
async def sub(ctx):
    sub_role = [958277060390965258
    # , #sub
    # 183800165767970820
    ] #life guard
    rank_roles = [
    869528040265363456, #grand champ
    869527980035153940, #champ
    869527795456442368, #diamond
    869527569760923658, #plat
    869527452257517589, # gold
    869527391351996417, #silver
    869527337702666242, #bronze
    # 892260316224839680, #freestyle
    # 695490219687804928, #poke
    # 843196839057948722 #party
    ]
    no_rank = []
    for guild in client.guilds:
        print(guild.name)
        sub_list = {}
        for roleId in sub_role:
            # skip if roles does not exist
            if guild.get_role(roleId) != None:
                for member in guild.get_role(roleId).members:
                    print(member.name)
                    found = False
                    for rankId in rank_roles:
                        if found: break
                        for memRole in member.roles:
                            if found: break
                            if rankId == memRole.id:
                                print('found', rankId, memRole.name)
                                found = True
                                #add rank to sub list if it does not exist
                                if rankId not in sub_list:
                                    sub_list[rankId] = []
                                #append member id to respective rank
                                sub_list[rankId].append(member.mention)
                    if not found:
                        no_rank.append(member.mention)
        print(sub_list)
        text = ''
        embedTitle='LESC Season Substitutes'
        embedVar = discord.Embed(title=embedTitle, color=0xffffff)

        for item in sub_list:
            embedVar.add_field(name=guild.get_role(item).name, value='\n'.join(sub_list[item]), inline=True)
        if len(no_rank)>0:
            embedVar.add_field(name='No Rank', value='\n'.join(no_rank), inline=True)
        if len(sub_list)>0:
            await ctx.send(embed=embedVar)
        embedVar.clear_fields

@client.command(brief='Strawberries🍓 or Grapes🍇?')
async def fruit(ctx):
    fruit_role_ids = [963451965084409907, #strawberry
        # 843196839057948722, #partygoers #temp
        963455568838791178] #, #grape

    fruit_stats = {}
    max_count = 0
    max = 0
    white = 0xffffff
    color = {}
    fruit_db={}
    teamname_list=[]
    # global team_db
    # for div in team_db['LESC3']:
    #     for entry in div:
    #         if entry['team'] not in teamname_list:
    #             teamname_list.append(entry['team'])
    stats = {}
    global standings_db
    # print(standings_db)
    for div in standings_db['LESC3']:
        for entry in standings_db['LESC3'][div]:
            if entry[1] not in stats:
                stats[entry[1]] = {'gw': entry[4], 'sp':entry[2],'sw':entry[3],'points':entry[5]}

    # print(teamname_list)
    print('stats from standings:',stats)
    fruit_totals = {}
    for ids in fruit_role_ids:
        fruit_totals[ids] = {'sp':0,'sw':0,'gw': 0, 'points':0,'participants':0}
    for guild in client.guilds:
        print(guild.name)
        for fruit_role_id in fruit_role_ids:
            if guild.get_role(fruit_role_id) != None:
                fruit_stats[fruit_role_id] = {}
                fruit_role = guild.get_role(fruit_role_id)
                color[fruit_role_id] = fruit_role.color
                print(fruit_role.name)
                count = len(fruit_role.members)
                for member in fruit_role.members:
                    if member.id not in fruit_db:
                        fruit_db[member.id] = {'team': '', 'fruit': [],'gw': 0, 'sp':0,'sw':0,'points':0}
                    for role in member.roles:
                        if role.name in stats:
                            fruit_db[member.id]['team'] = role.name
                            fruit_db[member.id]['gw'] = stats[role.name]['gw']
                            fruit_db[member.id]['sp'] = stats[role.name]['sp']
                            fruit_db[member.id]['sw'] = stats[role.name]['sw']
                            fruit_db[member.id]['points'] = stats[role.name]['points']
                            fruit_totals[fruit_role_id]['gw'] = fruit_totals[fruit_role_id]['gw'] + int(stats[role.name]['gw'])
                            fruit_totals[fruit_role_id]['sp'] = fruit_totals[fruit_role_id]['sp'] + int(stats[role.name]['sp'])
                            fruit_totals[fruit_role_id]['sw'] = fruit_totals[fruit_role_id]['sw'] + int(stats[role.name]['sw'])
                            fruit_totals[fruit_role_id]['points'] = fruit_totals[fruit_role_id]['points'] + int(stats[role.name]['points'])
                            fruit_totals[fruit_role_id]['participants'] = fruit_totals[fruit_role_id]['participants'] + 1


                print('count:', count)
                fruit_stats[fruit_role_id]['count'] = count
                fruit_stats[fruit_role_id]['participants'] = fruit_totals[fruit_role_id]['participants']
    print('fruit_db',fruit_db)
    print('fruit_stats:',fruit_stats)
    max_points = 0
    embedcolor = white
    for fruit in fruit_totals:
        for stat in fruit_totals[fruit]:
            if stat not in  ['count','participants'] and fruit in fruit_stats:
                denom = fruit_totals[fruit]['participants']
                if fruit_totals[fruit]['participants'] == 0:
                    denom = 1
                fruit_stats[fruit][stat] = round(fruit_totals[fruit][stat]/denom,1)
        if fruit_stats[fruit]['points'] > max_points:
            embedcolor = color[fruit]
            max_points = fruit_stats[fruit]['points']
        elif fruit_stats[fruit]['points'] == max_points:
            embedcolor = white

    print('fruit_totals',fruit_totals)
    print('fruit_stats',fruit_stats)

    stat_names = {'count': 'Total Votes','gw': 'Avg. Games Won', 'sp': 'Avg. Series Played','sw': 'Avg. Series Won','points': 'Avg. Points','participants': 'League Participants'}

    embedTitle='The Grape Debate'
    embedVar = discord.Embed(title=embedTitle, color=embedcolor)
    embedVar.set_footer(text='Results collected by strawberry poll')
    for fruit in fruit_stats:
        statlist=[]
        for stat in fruit_stats[fruit]:
            statlist.append(f'{stat_names[stat]}:    **{fruit_stats[fruit][stat]}**')
        embedVar.add_field(name=guild.get_role(fruit).name, value='\n'.join(statlist), inline=True)
    if len(fruit_stats)>0:
        await ctx.send(embed=embedVar)


@client.command(brief='Check bot latency')
async def ping(ctx):
    await ctx.send(f'Pong! {round(client.latency * 1000)} ms')

@client.command(brief='View the teams of a season',usage='[season #] [division name]',
    description='Defaults to the current season if no [arguments] are passed',
    help='EXAMPLE:\nTo view the US division for season 1 use,\n.season 1 US')
async def season(ctx,*args):
    division = [] #default to all
    season = 3 #default to current
    seaDiv = {
    1: {1:'US',2:'EU'},
    2: {1:'Upper',2:'Lower'},
    3: {1:'NA Upper', 2:'NA Lower', 3: 'EU Upper', 4:'EU Lower'}
    }
    for arg in args:
        if arg == '1':
            season = 1
        elif arg == '2':
            season = 2
        elif arg.lower() == 'us':
            division.append(1)
            season = 1
        elif arg.lower() == 'eu':
            division.append(2)
            season = 1
        elif arg.lower() == 'upper':
            division.append(1)
            season = 2
        elif arg.lower() == 'lower':
            division.append(2)
            season = 2
    # if division not specified, use both
    if len(division)<1:
        division = seaDiv[season].keys()
    d={}
    # d={1:'',2:''}
    for div in division:
        d[div] = ''

    embedTitle='LESC Season ' + str(season) + ' Teams'
    embedVar = discord.Embed(title=embedTitle, color=0xffffff)

    for team in team_db['LESC'+str(season)]:
        d[team['division']] = d[team['division']] + '\n' + team['team']
    print('d=\n',d)
    for div in division:
        embedVar.add_field(name=seaDiv[season][div] +' Division', value=d[div], inline=True)

    await ctx.send(embed=embedVar)

@client.command(brief='View team rosters',aliases=['team','roster','rosters'],usage='[season #] [division name]',
description='Defaults to the current season if no [arguments] are passed',
help='EXAMPLE:\nTo view the team rosters for the Season 1 US division use,\n.team 1 US')
async def teams(ctx,*args):
    print('command: teams')
    global team_db
    division = [] #default to all
    season = 3 #default to current
    argDiv = {'us': 1, 'eu' : 2, 'upper': 1, 'lower': 2}
    seaDiv = {
        1: {1:'US',2:'EU'},
        2: {1:'Upper',2:'Lower'},
        3: {1:'NA Upper', 2:'NA Lower', 3: 'EU Upper', 4:'EU Lower'}
        }
    for arg in args:
        if arg == '1':
            season = 1
        elif arg == '2':
            season = 2
        elif arg.lower() == 'eu':
            division.append(2)
            season = 1
        elif arg.lower() == 'us':
            division.append(1)
            season = 1
        elif arg.lower() == 'upper':
            division.append(1)
            season = 2
        elif arg.lower() == 'lower':
            division.append(2)
            season = 2

    # print(division)
    if len(division)<1:
        division = seaDiv[season].keys()

    embedTitle='LESC Season ' + str(season) + ' Teams'
    # print(division)
    # print(team_db['LESC'+str(season)])
    for div in division:
        embedVar = discord.Embed(title=embedTitle,description='**' + seaDiv[season][div] + ' Division**', color=0xffffff)
        for col in ['team','captain','teammate']:
            val = []
            for team in team_db['LESC'+str(season)]:

                if team['division'] == div:
                    # print(team)
                    val.append(team[col])

            embedVar.add_field(name=col.capitalize(), value='\n'.join(val), inline=True)
        await ctx.send(embed=embedVar)
        embedVar.clear_fields



@client.command(brief='View season standings',aliases=['results'],usage='[season #] [division name]',
description='Defaults to the current season if no [arguments] are passed',
help='EXAMPLE:\nTo view the standings of the Season 1 US division use,\n.season 1 US')
async def standings(ctx,*args):
    global standings_db
    division = [] #default to all
    season = 3 #default to current
    seaDiv = {
        1: {1:'US',2:'EU'},
        2: {1:'Upper',2:'Lower'},
        3: {1:'NA Upper', 2:'NA Lower', 3: 'EU Upper', 4:'EU Lower'}
        }
    for arg in args:
        if arg == '1':
            season = 1
        elif arg == '2':
            season = 2
        elif arg.lower() == 'eu':
            division.append(2)
            season = 1
        elif arg.lower() == 'us':
            division.append(1)
            season = 1
        elif arg.lower() == 'upper':
            division.append(1)
        elif arg.lower() == 'lower':
            division.append(2)

    if len(division)<1:
        division = seaDiv[season].keys()

    for div in division:
        matches = standings_db['LESC'+str(season)][div]
        title = '**LESC Season ' + str(season) + ' - '+ seaDiv[season][div] +' Standings**\n'
        string = ''
        temp = ''

        coln=len(matches[0])-1
        if season == 3:
            coln = coln +1
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

@client.command(description='View the LESC profile of yourself or the mentioned user',
    brief='View LESC profile of [user], defaults to self',aliases=['me'],usage='[@user]')
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
                    y=8

                except Exception as e:
                    msg = await log.send(e)
                    newcontent = 'save user to redis participants: '+ arg + '\n' + msg.content
                    await msg.edit(content=newcontent)
                    raise

            else:
                await ctx.send('No season roles')
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

# @client.command(aliases=['doc','data','stats','sheets'],brief='Link to LESC Google Sheet')
# async def sheet(ctx):
#     string= 'Click the link below to go to the offical LESC spreadsheet\n'
#     # season 1
#     # link='https://docs.google.com/spreadsheets/d/1jnsbvMoK2VlV5pIP1NmyaqZWezFtI5Vs4ZA_kOQcFII/edit#gid=1868244777'
#     # season 2
#     link = 'https://docs.google.com/spreadsheets/d/1DdgY8i-pKK8WoszvfrKUYEoy4I9f3qzUxaLumOo7Ptw/edit?usp=sharing'
#     # season 3
#     # link =
#     await ctx.send(string+link)

# TEMPORARILY REMOVED
# @client.command(brief="!Link to the LESC feedback form!")
# async def feedback(ctx):
#     string = f'Click the link below to give feedback on the LESC \n'
#     link = 'https://discord.com/api/oauth2/authorize?client_id=873361977991381043&permissions=223296&scope=bot'
#     block = """**LESC Season 2 is COMING SOON ™️ to a discord server near you!**
#
# We want to give you the best Season 2 that we can, and for that we need your help! We've compiled a survey that will help us find out what you want from the LESC, so that we can tweak the format of the competition and make it more fun for everyone. Please head to https://forms.gle/3VfB5nNuwakzSU178 to share your thoughts and opinions.
#
# This survey is for **EVERYONE**, it doesn't matter if you are a **Substitute**, **Commentator**, or **Viewer**, we want your feedback and ideas!
#
# **Two things to note:**
# Firstly, please be honest! We can't improve if we don't know how you lot feel.
# Secondly, we wont share any answers/information your provide outside of the commissioners, and your email addresses are not recorded by us."""
#     await ctx.send(block)

@client.command(brief="Get current time + [X hours]",
    usage='<# of hours to add to current time>',
    description='Easily schedule across time zones by just adding hours to the current time',
    help = '.time 1.5,  will respond with the time in 1 and a half hours')
async def time(ctx, hours=0.0):
    await ctx.reply(f'<t:{str(int(t.time()) + int(hours*3600))}>')

@client.command(brief="Link LESC profile to your discord",
    usage='[your name in google sheets if not the same as your Discord name]',
    description='In order to pull up your league stats in discord without searching your name, you will need to assign your name in the LESC google sheet to your discord account.')
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
@client.command(brief="Add a quote to your profile",
    usage='<"Your quote enclosed with double quotations">',
    description="Add some flavor to your profile with a quote")
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

@client.command(brief="Search current season matches of a team",
    aliases=['match','matchup','matchups'],
    usage='<team name search>',
    description='Must search a team name from the current season to pull up matches')
async def matches(ctx, arg = ''):
    # season = 1 #default
    # seaDiv = { 1: {1:'US',2:'EU'}, 2: {1:'Upper',2:'Lower'} }
    seaDiv = {
        1: {1:'US',2:'EU'},
        2: {1:'Upper',2:'Lower'},
        3: {1:'NA Upper', 2:'NA Lower', 3: 'EU Upper', 4:'EU Lower'}
        }
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
    for div in matches_db['LESC3']:

        for match in matches_db['LESC3'][div]:
            if searchTerm.lower() in match['home'].lower() or searchTerm.lower() in match['away'].lower():
                for m in max:
                    if max[m] < len(match[m]):
                        max[m] = len(match[m])
                prepList.append(match)
    head = []
    for key in max:
        head.append(header[key] + ' '*(max[key]-len(header[key])))
    output = 'LESC Season 3\n' + '  '.join(head)
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

@client.command(brief="Return a list of live streamers or the next scheduled stream",
    help='If you would like to be added or removed from the list, contact KarmaKredits',
    aliases = ['stream', 'streamers', 'streamer', 'twitch', 'ttv'])
async def streams(ctx):
    msg = await ctx.send('Fetching dem streamers...')
    tw.getToken()
    user_list = tw.getUserIDFromLogin('&login='.join(tw.streamerlist))
    embed = discord.Embed(title='LESC Community Streams', color=0xffffff)
    # embed.set_footer(text = 'DM KarmaKredits to be added to streamer list')
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

@client.command(brief="Return a list of scheduled matches",
    help='List the future matches to be played with local time and teams')
async def schedule(ctx):
    schedule = checkForMatches()
    # print(schedule)
    matchList = []
    for item in schedule:
        # print(item)
        matchList.append(f"<t:{item['unix']}> \t**{item['info']['home']}**  vs  **{item['info']['away']}**")
    text = '\n'.join(matchList)
    # print(text)
    title = '**Scheduled Matches**\n'
    await ctx.send(content = title + text)


async def twitchAlerts():
    global last_sorted_list
    global last_live
    global guildTEST
    global guildLESC
    print('twitchAlert check')
    tw.getToken()
    user_list = tw.getUserIDFromLogin('&login='.join(tw.streamerlist))
    embed = discord.Embed(title='LESC Community Streams', color=0xffffff)
    # embed.set_footer(text = 'DM KarmaKredits to be added to streamer list')
    now = datetime.utcnow()
    list = []
    lesc_live = []
    other_live = []
    role_live = []
    role_LESC = []
    live=False
    searchTerms = ['lesc','league of extraordinary soccer cars']
    next_time = None
    for user in user_list:
        # print(user['login'])
        sched = tw.getScheduleFromUserID(user['id'])
        if sched == None: sched = []
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
            live=True
            # LIVE LESC Stream
            foundTerm = False
            for term in searchTerms:
                if term in stream[0]['title'].lower():
                    foundTerm = True
                    break

            if foundTerm:
                lesc_live.append({'time' : dt_start, 'data' : {'name':user_name, 'value':'[' + title + '](https://www.twitch.tv/' + login +')\n'+game_name}})
                role_LESC.append(login)
                # print(user_name, 'added to LESC')
            else:
                other_live.append({'time' : dt_start, 'data' : {'name':user_name, 'value':'[' + title + '](https://www.twitch.tv/' + login +')\n'+game_name}})
                role_live.append(login)
                # print(user_name, 'added to live')

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

    print('======================================================')
    print('role_LESC:',role_LESC)
    print('role_live:',role_live)
    #manage roles
    await roleCheck(role_LESC, role_live)
    print('----------------------------------------------------')
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
    if live and ((next_time <30 and next_time >= 0) or (sorted_list_check != last_sorted_list and last_sorted_list != [])):
        print('next_time <60 and next_time > 0', next_time)
        print('sorted_list != last_sorted_list and last_sorted_list != []',sorted_list_check, last_sorted_list)
        await log.send(embed=embed)

    last_sorted_list = sorted_list_check

    print('lesc_live:\n',lesc_live)
    print('last_live:\n',last_live)
    if len(lesc_live)>0 and (lesc_live != last_live):
        print('diff')
        send = False
        embed2 = discord.Embed(title='LESC LIVE', color=0xffffff)
        # embed2.set_footer(text = 'DM KarmaKredits to be added to streamer list')
        for item in lesc_live:
            if (item not in last_live):
                print('item not in last_live')
                embed2.add_field(name = item['data']['name'], value = item['data']['value'], inline = True)
                send = True
        if send:
            await log.send(embed=embed2)
            if lescLiveChannel != None:
                await lescLiveChannel.send(embed=embed2)
    last_live = lesc_live

    schedule = checkForMatches()

    # max time to wait 10 minutes
    if next_time > 600: next_time = 600
    return next_time
    # return 90

async def roleCheck(role_LESC = [], role_live = []):
    # print('args: ', role_LESC, role_live)
    global guildTEST
    global guildLESC
    role = {
        guildTESTID: {'live' : 915021503731478581, 'lesc' : 915021759667908608, 'guild': guildTEST},
        guildLESCID: {'live' : 915269257904939039, 'lesc' : 915268612137295892, 'guild': guildLESC}
    }

    # print(guildLESC)
    # print(guildTEST)
    for twName in tw.streamDiscordId:
        discordId = tw.streamDiscordId[twName]
        # print(twName,discordId)
        for guildID in [guildTESTID, guildLESCID]:
            # print('guild: ', role[guildID]['guild'])
            try:
                liveRole = client.get_guild(guildID).get_role(role[guildID]['live'])
                lescRole = client.get_guild(guildID).get_role(role[guildID]['lesc'])
                # print(liveRole)
                # print(lescRole)
                member = await role[guildID]['guild'].fetch_member(discordId)
                # print('member: ', member)
                # print('member roles: ', member.roles)
                # await log.send(member)
                # guildLESC.get_member(discordId)
                if twName in role_LESC:
                    # print('LESC in title')
                    # await log.send(twName + ' is LESC')
                    try:
                        await member.add_roles(lescRole)
                    except Exception as e:
                        # print('lesc add', e)
                        # await log.send(e)
                        pass
                    try:
                        await member.remove_roles(liveRole)
                    except Exception as e:
                        # print('live remove', e)
                        # await log.send(e)
                        pass
                elif twName in role_live:
                    # print('is LIVE')
                    # await log.send(twName + ' is Live')
                    try:
                        await member.add_roles(liveRole)
                        # print('role')
                    except Exception as e:
                        # print('live add', e)
                        # await log.send(e)
                        pass
                    try:
                        await member.remove_roles(lescRole)
                    except Exception as e:
                        # print('lesc remove', e)
                        # await log.send(e)
                        pass
                else:
                    # print('Not live')
                    # await log.send(twName + ' Not Live')
                    try: await member.remove_roles(liveRole)
                    except Exception as e:
                        # print('live remove', e)
                        # await log.send(e)
                        pass
                    try: await member.remove_roles(lescRole)
                    except Exception as e:
                        # print('lesc remove', e)
                        # await log.send(e)
                        pass
            except Exception as e:
                # print('exception guild:', guildID, '\n', e)
                # await log.send(e)
                pass
    # live_memebers = guildLESC.get_role(liveRoleID).members
    # lesc_members = guildLESC.get_role(lescRoleID).members


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

def checkForMatches():
    #check for scheduled matches
    now=datetime.utcnow()
    # print('UTC',now)
    # print('EST',now + timedelta(hours=-5))
    # print('EDT',now + timedelta(hours=-4))
    # print('ET',datetime.now())
    # print('CET',now + timedelta(hours=1))
    zoneOffset = {'ET': +4,'CET': -1} #local to utc
    meridiemOffset = {'AM': 0, 'PM': 12,'': 0}
    monthNumber = {'Apr': 4, 'May': 5, 'Jun': 6}
    schedule = []
    future = False
    for div in matches_db['LESC3']:
        for match in matches_db['LESC3'][div]:

            # print('Date: ', match['date'],'Time: ',match['time'])
            # print(2022,int(match['date'][3:5]),int(match['date'][0:2]),int(match['time'][0:2]),int(match['time'][3:5]))
            x = re.findall("(\d{1,2})-(\w{3})", match['date'])
            # print(x)
            day, month = x[0]
            day = int(day)
            y = re.findall("(\d{1,2}):(\d\d)\s([AP]?[M]?)\s?(\w{2,3})", match['time'])
            # print(y, len(y[0]))
            hour, minute, meridiem, zone = y[0]
            hour = int(hour)
            minute = int(minute)
            try:
                matchdatetime = datetime(2022,monthNumber[month],day,hour,minute)
                # print(matchdatetime)
                matchdatetimeUTC = matchdatetime + timedelta(hours=zoneOffset[zone]+meridiemOffset[meridiem])
                # print(matchdatetimeUTC)
                future = now < matchdatetimeUTC
                unixtime = calendar.timegm(matchdatetimeUTC.utctimetuple())
                # print(t.mktime(matchdatetimeUTC.utctimetuple())) #shows utc time as local

            except Exception as e:
                # raise
                print(e)
                pass
            # print('Match datetime: ',matchdatetime)
            if future:
                schedule.append({'unix': unixtime, 'info': match})


    # print(schedule)
    # for item in schedule:
    #     print(item)
    # sort schedule

    scheduleSorted = []
    cnt = 0
    while len(schedule)>0:
        if cnt>50: break
        cnt = cnt + 1
        minUnix = 9999999999
        minInfo = {}
        minIndex = 0

        for i in range(len(schedule)):
            if schedule[i]['unix']<minUnix:
                minUnix = schedule[i]['unix']
                # minInfo = schedule[i]['info']
                minIndex = i
        scheduleSorted.append(schedule.pop(minIndex))
    # print('sorted')
    # for item in scheduleSorted:
    #     print(item['unix'], item['info']['date'])
    # print(scheduleSorted)
    return scheduleSorted


if __name__ == '__main__':
    client.run(TOKEN)
