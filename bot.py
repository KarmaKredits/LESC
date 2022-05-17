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
rc=redisDB()
team_db={}
standings_db = {}
matches_db = {}
participant_db = {}
LESC3_DB = []

async def updateFromGoogleSheets():
    global LESC3_DB
    response = ''
    try:
        # get db info from googleSheets
        print('loading data from google sheets...')
        divisions = [1,2,3,4]
        divisionNames = ['NA Upper','NA Lower','EU Upper', 'EU Lower']
        divisionKey = ['naupper','nalower','euupper', 'eulower']

        updated_db = googleSheets.getDataFromGoogleSheets() #current season only
        #sync existing and new data
        # print('LESC3_DB',LESC3_DB)

        if updated_db is not None:
            # rc1 = redisDB()
            response = 'Unable to update Redis, contact KarmaKredits'
            rc.setValue(key='lesc3_db',value=updated_db) # overwrite
            LESC3_DB = updated_db

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
    global LESC3_DB
    # global team_db
    # print(LESC3_DB)
    # print(LESC3_DB)
    print('team_db')
    team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)
    # global standings_db
    print('standings_db')
    standings_db['LESC3'] = LESC3.formatStandings(LESC3_DB)
    # global matches_db
    print('matches_db')
    matches_db['LESC3'] = LESC3.getMatches(LESC3_DB)



@client.event
async def on_ready():
    print('LOADING...')
    await client.change_presence(activity=discord.Activity(name=".help",type=discord.ActivityType.watching))

    client.load_extension('cogs.commissioners')
    client.load_extension('cogs.profile')
    client.load_extension('cogs.league')

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
        team_db['LESC1'] = googleSheets.formatRosters(LESC1_DB)
        team_db['LESC2'] = googleSheets.formatRosters(LESC2_DB)
        team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)
        rc.setValue(key='rosters',value=team_db)

        print('formating standings...')
        step = 'standings'
        global standings_db
        standings_db['LESC1'] = googleSheets.formatStandings(LESC1_DB)
        standings_db['LESC2'] = googleSheets.formatStandings(LESC2_DB)
        standings_db['LESC3'] = LESC3.formatStandings(LESC3_DB)
        # rc.setValue(key='standings',value=standings_db)
        print('playoffs')
        playoffList = {}
        playoffList['LESC1'] = googleSheets.teamsInPlayoffs(LESC1_DB)
        playoffList['LESC2'] = googleSheets.teamsInPlayoffs(LESC2_DB)
        playoffList['LESC3'] = LESC3.teamsInPlayoffs(LESC3_DB)

        print('awards')
        awardsTable = {}
        awardsTable['LESC1']  = googleSheets.getAwards(LESC1_DB)
        # awardsTable['LESC2']  = []
        awardsTable['LESC2']  = googleSheets.getAwards(LESC2_DB)
        awardsTable['LESC3'] = []
        print('generating profiles...')
        step = 'profiles'
        # global player_db
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

        rc.setValue('participants',participant_db)
        # print(participant_db)
        # print(participant_db['sassybrenda'])
        # print(participant_db['karmakredits'])

        print('formating matches...')
        step = 'matches'
        global matches_db
        # matches_db['LESC1'] = googleSheets.getMatches(LESC1_DB)
        # matches_db['LESC2'] = googleSheets.getMatches(LESC2_DB)
        matches_db['LESC3'] = LESC3.getMatches(LESC3_DB)



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
        # print(me)
        # await log.send(me.mention)
        # members = await guildTEST.fetch_members(limit=150).flatten()
        # print(members)
        # for item in guildTEST.members:
        #     print(item)

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
    # global standings_db
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


@client.command(brief='Link to invite this bot your own server')
async def invite(ctx):
    string = f'Click the link below to invite {client.user.name} to your server \n'
    link = 'https://discord.com/api/oauth2/authorize?client_id=873361977991381043&permissions=223296&scope=bot'
    await ctx.send(string+link)


@client.command(brief="Get current time + [X hours]",
    usage='<# of hours to add to current time>',
    description='Easily schedule across time zones by just adding hours to the current time',
    help = '.time 1.5,  will respond with the time in 1 and a half hours')
async def time(ctx, hours=0.0):
    await ctx.reply(f'<t:{str(int(t.time()) + int(hours*3600))}>')


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
    help='List the future matches to be played with local time and teams',
    aliases=['games'])
async def schedule(ctx):
    schedule = checkForMatches()
    # print(schedule)
    matchList = []
    categoryList = []
    catN = 0
    for i in range(len(schedule)):
        if i == 0:
            categoryList.insert(catN,[schedule[i]])
        else:
            if (schedule[i]['unix']-schedule[i-1]['unix'])/3600 > 8:
                catN = catN + 1
                categoryList.insert(catN,[schedule[i]])
            else:
                categoryList[catN].append(schedule[i])
    # print(categoryList)

    # for item in schedule:
    #     # print(item)
    #     matchList.append(f"<t:{item['unix']}> \t**{item['info']['home']}**  vs  **{item['info']['away']}**")
    # text = '\n'.join(matchList)
    # print(text)
    title = '**Scheduled Matches**'

    catText = ''

    for group in categoryList:
        catText = catText + f"\n\n__Games starting <t:{group[0]['unix']}:R>__\n"
        # print('new group')
        groupMatches = []
        for item in group:
            # print('item',item)
            groupMatches.append(f"<t:{item['unix']}> \t**{item['info']['home']}**  vs  **{item['info']['away']}**")
        # print('group',groupMatches)
        catText = catText + '\n'.join(groupMatches)


    await ctx.send(content = title + catText)


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
    matchdb = LESC3.getMatches(rc.getValue('lesc3_db'))
    # print(matchdb)
    for div in matchdb:
        for match in matchdb[div]:

            x = re.findall("(\d{1,2})-(\w{3})", match['date'])
            y = re.findall("(\d{1,2}):(\d\d)\s([AP]?[M]?)\s?(\w{2,3})", match['time'])
            # print(x)
            # print(y)

            if len(x) > 0 and len(y) > 0:
                day, month = x[0]
                day = int(day)
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
    diff = []
    for i in range(1,len(scheduleSorted)):
        diff.append((scheduleSorted[i]['unix'] - scheduleSorted[i-1]['unix'])/3600)
    # print(diff)

    # mean_diff = sum(diff) / len(diff)
    # print(diff)
    # print(mean_diff)
    # for item in diff:
    #     if item > mean_diff:
    #         print('-')
    #     print(item)

    return scheduleSorted


if __name__ == '__main__':
    client.run(TOKEN)
