import urllib.request
import json
import csv
import pandas as pd

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