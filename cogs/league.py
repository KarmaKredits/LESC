import discord
from discord.ext import commands
from bot import lescTitle
from redisDB import redisDB
import LESC3
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



def setup(client):
    client.add_cog(League(client))
