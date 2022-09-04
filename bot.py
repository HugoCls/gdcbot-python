from discord.ext import commands
import pandas as pd
import os
import urllib.request
import json
import csv
import discord

def get_players():
    with open("key.txt") as f:
        my_key = f.read().rstrip("\n")
        
        base_url = "https://api.clashroyale.com/v1"
        
        endpoint_riverrace = "/clans/%23UURJ9CG/currentriverrace"
        
        request_riverrace= urllib.request.Request(
                base_url+endpoint_riverrace,
                None,
                {
                    "Authorization": "Bearer %s" % my_key
                }
            )
        response_riverrace = urllib.request.urlopen(request_riverrace).read().decode("utf-8")
        
        dict_riverrace=json.loads(response_riverrace)
        
        endpoint_clan = "/clans/%23UURJ9CG"
        
        request_clan = urllib.request.Request(
                base_url+endpoint_clan,
                None,
                {
                    "Authorization": "Bearer %s" % my_key
                }
            )
        response_clan = urllib.request.urlopen(request_clan).read().decode("utf-8")
        
        dict_clan=json.loads(response_clan)
        
        members_tags=[]
        
        for member in dict_clan["memberList"]:
            members_tags.append(member["tag"])
            
        clan_dict={}
        for member in dict_clan["memberList"]:
            clan_dict[member["tag"]]={"name":member["name"],"discord":""}
            
    clan_dict=add_discords2(clan_dict)
    
    afk_players=[]
    for player in dict_riverrace["clan"]["participants"]:
        if player["decksUsedToday"]<4 and player["tag"] in members_tags:
            afk_players.append(player["tag"])
    
    return(afk_players,clan_dict)

def add_discords1(clan_dict):
    discords=[]
    with open('discords.txt', 'r') as f:
        reader = csv.reader(f,delimiter=':')
        for row in reader:
            discords.append(tuple(row))
    for i in range(len(discords)):
        (cr_id,disc_id)=discords[i]
        if cr_id in clan_dict.keys():
            clan_dict[discords[i][0]]['discord']=disc_id
    return(clan_dict)

def add_discords2(clan_dict):
    df=pd.read_csv('clan.csv')
    ids=clan_dict.keys()
    for i in range(len(df)):
        line=df.iloc[i]
        if line['CR id'] in ids:
            clan_dict[line['CR id']]['discord']=line['Discord']
    return(clan_dict)

def nice_format(cr_id):
    L=[]
    for i in range(len(cr_id)):
        L.append(cr_id[i])
    while True:
        j=0
        for i in range(len(L)):
            if L[i]=="#":
                del(L[i])
                j=1
                break
        if j==0:
            break
    final_id=["#"]
    for i in range(len(L)):
        final_id.append(L[i])
    new_id=''.join(e for e in final_id)
    return(new_id)

def write_csv():
    afk_players,clan_dict=get_players()
    L_cr_ids=list(clan_dict.keys())
    L_names=[]
    for i in range(len(L_cr_ids)):
        cr_id=L_cr_ids[i]
        name=clan_dict[cr_id]['name']
        L_names.append(name)
    
    L_discord_ids=['' for i in range(len(L_names))]

    df = pd.DataFrame(list(zip(L_cr_ids,L_names, L_discord_ids)), columns =['CR id','Name','Discord'])
    
    df.to_csv('empty_clan.csv', encoding='utf-8')
    return(df)

client=commands.Bot(intents = discord.Intents.all(),command_prefix = '-')

@client.event
async def on_ready():
    print('BOT Gdc is ready.')

@client.command()
async def cr_id(ctx,user_cr_id,user_disc_id=None):
    user_cr_id=nice_format(user_cr_id)
    if len(user_cr_id)>10:
        await ctx.reply('Wrong CR-id, sorry mate.')
    else:
        if user_disc_id==None:
            user_disc_id=str(ctx.author.id)
        
        df = pd.read_csv('clan.csv')
        
        afk_players,clan_dict=get_players()
        
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
    afk_players,clan_dict=get_players()
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
    afk_players,clan_dict=get_players()
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

def read_token():
    with open('token.txt','r') as f:
        lines=f.readlines()
        return(lines[0].strip())
"""
TOKEN=read_token()

client.run(TOKEN)  
"""
client.run(os.environ['DISCORD_TOKEN'])
