import discord
from discord.ext import commands
from bot import lescTitle
from redisDB import redisDB
rc=redisDB()
logChannel=866129852708814858

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.log = self.client.get_channel(logChannel)



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
        # print(participant_db)
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
        if not_found:
            await ctx.message.reply('Profile not found')

    @commands.command(brief="Link LESC profile to your discord",
        usage='[your name in google sheets if not the same as your Discord name]',
        description='In order to pull up your league stats in discord without searching your name, you will need to assign your name in the LESC google sheet to your discord account.')
    async def claim(self, ctx, arg=None):
        # log = self.client.get_channel(logChannel)
        print('claim command used')
        to_send = ''
        if arg == None:
            print('no arg')
            arg = ctx.author.display_name
            to_send = 'No name given, using Discord display name: ' + str(ctx.author.display_name) + '\n'
        arg = arg.lower()
        participant_db = rc.getValue('participants')

        if arg in participant_db:
            print('arg found')
            participant_db[arg]['id']=ctx.author.id
            link_text = '<@' + str(ctx.author.id) + '> linked with ' + participant_db[arg]['player']
            to_send = to_send + 'Profile name found! ' + link_text
            try:
                rc.setValue('participants',participant_db)
                # await log.send(link_text)
                await self.log.send(link_text)
            except Exception as e:
                msg = await self.log.send(e)
                newcontent = 'claim redis participants: '+ arg + '\n' + msg.content
                await msg.edit(content=newcontent)
                raise
        else:
            print(arg + ' not found')
            to_send = to_send + arg + ' not found'
        await ctx.message.reply(to_send)

    @commands.command(brief="Add a quote to your profile",
        usage='<"Your quote enclosed with double quotations">',
        description="Add some flavor to your profile with a quote")
    async def quote(self, ctx, *args):
        response = ''
        if len(args) == 0:
            print('None')
            response = 'No quote detected. use this format:\n.quote "your quote here, enclosed by double-quotation marks"'
        elif len(args)>0:
            found=False
            participant_db = rc.getValue('participants')
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
                        await self.log.send('<@' + str(ctx.author.id) + '> has set ' + player + ' quote to: ' + quote)
                    except Exception as e:
                        msg = await self.log.send(e)
                        newcontent = 'quote to redis participants: '+ arg + '\n' + msg.content
                        await msg.edit(content=newcontent)
                        raise
            if not found:
                response = 'You must first claim your profile, please use the ".claim <profile name>" command to claim your profile'
        if len(response)>1:
            await ctx.message.reply(response)


def setup(client):
    client.add_cog(Profile(client))
