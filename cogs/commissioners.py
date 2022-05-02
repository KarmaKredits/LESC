import discord
from discord.ext import commands
import bot

class Commissioners(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(brief='Update DB from Google Sheets (Commissioners ONLY)')
    async def update(self, ctx):
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
            response = await bot.updateFromGoogleSheets()
            if response == 'Update Successful':
                bot.variable_update()
                print('variable update')
            await msg.edit(content=response)

def setup(client):
    client.add_cog(Commissioners(client))
