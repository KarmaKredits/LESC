import discord
from discord.ext import commands
from bot import lescTitle
from redisDB import redisDB
rc=redisDB()

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(description='View the LESC profile of yourself or the mentioned user',
        brief='View LESC profile of [user], defaults to self',aliases=['me'],usage='[@user]')
    async def profile(self, ctx, arg = None):
        if arg == None:
            arg = ctx.author.display_name #mention
            print(arg)
        elif len(arg)<3:
            await ctx.message.reply('Please use at least 3 characters for profile name search')
            return
        not_found = True
        # global participant_db
        participant_db = rc.getValue('participants')
        print(participant_db)
        for playerkey in participant_db:
            if not not_found: break
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
        # season_sub= ['860144876866502666', # S1 US Sub
        # '860145226224107550',# S1 EU Sub
        # '843196839057948722'] #test
        # award_sub=['869417365975224340', # S1 Participant
        # '695490219687804928'] #test
        if not_found:
            # if arg.lower()==ctx.author.display_name.lower():
            #     season_list = ['-']
            #     award_list = ['-']
            #     for role in ctx.author.roles:
            #         if str(role.id) in season_sub:
            #             print('season')
            #             print(role.name)
            #             season_list.insert(0,role.name)
            #         if str(role.id) in award_sub:
            #             print('award')
            #             print(role.name)
            #             award_list.insert(0,role.name)
            #     if len(season_list) or len(award_list):
            #         key=arg.lower()
            #         participant_db[key] = {'player':arg,
            #             'season':season_list,'teams':['-'],'teammates':['-'],'awards':award_list,'id':0,'quote':''}
            #         if len(participant_db[key]['season'])>1 and '-' in participant_db[key]['season']: participant_db[key]['season'].remove('-')
            #         if len(participant_db[key]['awards'])>1 and '-' in participant_db[key]['awards']: participant_db[key]['awards'].remove('-')
            #         embedVar = discord.Embed(title=arg, color=0xffffff)
            #         embedVar.add_field(name='Seasons',value='\n'.join(participant_db[key]['season']),inline=True)
            #         embedVar.add_field(name='Teams',value='\n'.join(participant_db[key]['teams']),inline=True)
            #         embedVar.add_field(name='Teammates',value='\n'.join(participant_db[key]['teammates']),inline=True)
            #         embedVar.add_field(name='Awards',value='\n'.join(participant_db[key]['awards']),inline=True)
            #         embedVar.set_footer(text=lescTitle)
            #         await ctx.send(embed=embedVar)
            #         try:
            #             rc.setValue('participants',participant_db) #save user to db
            #             y=8
            #
            #         except Exception as e:
            #             msg = await log.send(e)
            #             newcontent = 'save user to redis participants: '+ arg + '\n' + msg.content
            #             await msg.edit(content=newcontent)
            #             raise
            #
            #     else:
            #         await ctx.send('No season roles')
            # else:
            await ctx.message.reply('Profile not found')


def setup(client):
    client.add_cog(Profile(client))
