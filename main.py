import discord
from discord.ext import commands, tasks
from itertools import cycle
import gdcbot as gdc
import pandas as pd
import os

"""
def read_token():
    with open('token.txt','r') as f:
        lines=f.readlines()
        return(lines[0].strip())

TOKEN=read_token()
"""
client=commands.Bot(command_prefix = '-')

@client.event
async def on_ready():
    #check_gdc.start()
    print('BOT Gdc is ready.')

@client.command()
async def cr_id(ctx,user_cr_id,user_disc_id=None):
    user_cr_id=gdc.nice_format(user_cr_id)
    if len(user_cr_id)>10:
        await ctx.reply('Wrong CR-id, sorry mate.')
    else:
        if user_disc_id==None:
            user_disc_id=str(ctx.author.id)
        
        df = pd.read_csv('clan.csv')
        
        afk_players,clan_dict=gdc.get_players()
        
        ids=clan_dict.keys()
        
        user_name='unspecified'
        if user_cr_id in ids:
            user_name=clan_dict[user_cr_id]['name']

        df2 = pd.DataFrame(list(zip([user_cr_id],[user_name], [user_disc_id])), columns =['CR id','Name','Discord'])
        
        df=df.append(df2,ignore_index=True)
        df.to_csv('clan.csv', encoding='utf-8')
        
        await ctx.reply(user_name+':<@'+str(user_disc_id)+'>, saved.')
    await ctx.message.delete()

@client.command()
async def clear(ctx):
    await ctx.message.delete()
    await ctx.channel.purge(limit=100)

@client.command()
async def Hello(ctx):
    await ctx.reply('test')
    await ctx.message.delete()

@client.command()
async def ping(ctx):
    sentence1='| '
    sentence2=''
    afk_players,clan_dict=gdc.get_players()
    for player in afk_players:
        if player in clan_dict.keys():
            sentence1+=clan_dict[player]['name']+' | '
            if clan_dict[player]['discord']!='':
                sentence2+=' <@'+str(clan_dict[player]["discord"])+'> '
    sentence=sentence2+'\nIl vous reste des combats!'
    await ctx.reply(sentence)
    await ctx.message.delete()


@client.command()
async def check_disc(ctx):
    afk_players,clan_dict=gdc.get_players()
    cr_ids=clan_dict.keys()
    df=pd.read_csv('clan.csv')
    sentence=''
    
    count=0
    for cr_id in cr_ids:
        if cr_id not in list(df['CR id']):
            sentence+=clan_dict[cr_id]['name']+', '
            count+=1
    
    if sentence!='':
        if count>1:
            sentence+='ne sont pas dans la base de données.'
        else:
            sentence+="n'est pas dans la base de données."
    else:
        sentence='Tous les joueurs ont leur discord renseigné.'
        
    await ctx.reply(sentence)
    await ctx.message.delete()
    
client.run(os.environ['DISCORD_TOKEN'])