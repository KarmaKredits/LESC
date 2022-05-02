import discord
from discord.ext import commands
from bot import lescTitle
from redisDB import redisDB
rc=redisDB()
logChannel=866129852708814858

class League(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.log = self.client.get_channel(logChannel)




        
def setup(client):
    client.add_cog(League(client))
