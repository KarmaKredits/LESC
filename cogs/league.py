import discord
from discord.ext import commands
from bot import lescTitle
from redisDB import redisDB
import LESC3
import googleSheets
rc=redisDB()
logChannel=866129852708814858

class League(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.log = self.client.get_channel(logChannel)


    @commands.command(brief="Search current season matches of a team",
        aliases=['match','matchup','matchups'],
        usage='<team name search>',
        description='Must search a team name from the current season to pull up matches')
    async def matches(self, ctx, arg = ''):
        # season = 1 #default
        # seaDiv = { 1: {1:'US',2:'EU'}, 2: {1:'Upper',2:'Lower'} }
        LESC3_DB = rc.getValue('lesc3_db')
        matches_db = {}
        # matches_db['LESC1'] = googleSheets.getMatches(LESC1_DB)
        # matches_db['LESC2'] = googleSheets.getMatches(LESC2_DB)
        matches_db['LESC3'] = LESC3.getMatches(LESC3_DB)
        seaDiv = {
            1: {1:'US',2:'EU'},
            2: {1:'Upper',2:'Lower'},
            3: {1:'NA Upper', 2:'NA Lower', 3: 'EU Upper', 4:'EU Lower'}
            }
        if arg == '':
            await ctx.message.reply('Please include part of team name you wish to lookup. For example,**.matches kimchi**, to look up matches for the "Kimchi Tacos"')
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


    @commands.command(brief='View team rosters',aliases=['team','roster','rosters'],usage='[season #] [division name]',
    description='Defaults to the current season if no [arguments] are passed',
    help='EXAMPLE:\nTo view the team rosters for the Season 1 US division use,\n.team 1 US')
    async def teams(self, ctx,*args):
        print('command: teams')

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
        #load correct db
        team_db = {}
        if season == 1:
            LESC1_DB = rc.getValue('lesc_db') #LESC1
            team_db['LESC1'] = googleSheets.formatRosters(LESC1_DB)
        elif season == 2:
            LESC2_DB = rc.getValue('lesc2_db') #LESC2
            team_db['LESC2'] = googleSheets.formatRosters(LESC2_DB)
        elif season == 3:
            LESC3_DB = rc.getValue('lesc3_db')
            team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)


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

    @commands.command(brief='View season standings',aliases=['results'],usage='[season #] [division name]',
    description='Defaults to the current season if no [arguments] are passed',
    help='EXAMPLE:\nTo view the standings of the Season 1 US division use,\n.season 1 US')
    async def standings(self, ctx,*args):
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
        standings_db = {}
        if season == 1:
            LESC1_DB = rc.getValue('lesc_db') #LESC1
            standings_db['LESC1'] = googleSheets.formatStandings(LESC1_DB)
        elif season == 2:
            LESC2_DB = rc.getValue('lesc2_db') #LESC2
            standings_db['LESC2'] = googleSheets.formatStandings(LESC2_DB)
        elif season == 3:
            LESC3_DB = rc.getValue('lesc3_db')
            standings_db['LESC3'] = LESC3.formatStandings(LESC3_DB)


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

    @commands.command(brief='View the teams of a season',usage='[season #] [division name]',
        description='Defaults to the current season if no [arguments] are passed',
        help='EXAMPLE:\nTo view the US division for season 1 use,\n.season 1 US')
    async def season(self, ctx,*args):
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

        team_db = {}
        if season == 1:
            LESC1_DB = rc.getValue('lesc_db') #LESC1
            team_db['LESC1'] = googleSheets.formatRosters(LESC1_DB)
        elif season == 2:
            LESC2_DB = rc.getValue('lesc2_db') #LESC2
            team_db['LESC2'] = googleSheets.formatRosters(LESC2_DB)
        elif season == 3:
            LESC3_DB = rc.getValue('lesc3_db')
            team_db['LESC3'] = LESC3.formatRosters(LESC3_DB)

        for team in team_db['LESC'+str(season)]:
            d[team['division']] = d[team['division']] + '\n' + team['team']
        # print('d=\n',d)
        for div in division:
            embedVar.add_field(name=seaDiv[season][div] +' Division', value=d[div], inline=True)

        await ctx.send(embed=embedVar)

    @commands.command(brief='List available subs',
        aliases=['subs','substitute','substitutes'])
    async def sub(self, ctx):
        sub_role = [958277060390965258 #sub
        # ,  183800165767970820 #life guard
        ]
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
        for guild in self.client.guilds:
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
                                    sub_list[rankId].append(f'{member.mention} {member}')
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

def setup(client):
    client.add_cog(League(client))
