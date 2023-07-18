import requests
from lxml import etree
from time import sleep

def request(msg, slp=2):
    '''A wrapper for robust https requests'''
    status_code = 500 
    while status_code != 200:
        sleep(slp) # Avoid pinging the server too often to not get blacklisted
        try:
            r = requests.get(msg)
            status_code = r.status_code
            if status_code != 200:
                print(f"Server Error! Response code {status_code}. Retrying...")
        except:
            print("An exceptions has occurred, probably momentary loss of connection. Waiting for a second...")
            sleep(1)
    return r

# Changed the sleep time in the request call to 0 compared to the scraping run to avoid artificially inflating response time

def retrieve_game_info(game_ids):

    id_list = ','.join(str(game_id) for game_id in game_ids)
    url = f'https://boardgamegeek.com/xmlapi2/thing?id={id_list}&stats=1'
    response = request(url, 0)
    return response.content

def parse_bgg_xml(xml_data):
    
    game_info = []
    
    root = etree.fromstring(xml_data)

    for item in root.xpath('//item'):
        id = item.xpath('@id')[0]
        name = item.xpath('.//name[@type="primary"]/@value')[0] if bool(item.xpath('.//name[@type="primary"]/@value')) else None
        #thumbnail = item.xpath('thumbnail/text()')[0] if bool(item.xpath('thumbnail/text()')) else None
        image = item.xpath('image/text()')[0] if bool(item.xpath('image/text()')) else None
        description = item.xpath('description/text()')[0] if bool(item.xpath('description/text()')) else None
        year_published = item.xpath('.//yearpublished/@value')[0] if bool(item.xpath('.//yearpublished/@value')) else None
        min_players = item.xpath('.//minplayers/@value')[0] if bool(item.xpath('.//minplayers/@value')) else None
        max_players = item.xpath('.//maxplayers/@value')[0] if bool(item.xpath('.//maxplayers/@value')) else None
        #playing_time = item.xpath('.//playingtime/@value')[0] if bool(item.xpath('.//playingtime/@value')) else None
        min_playtime = item.xpath('.//minplaytime/@value')[0] if bool(item.xpath('.//minplaytime/@value')) else None
        max_playtime = item.xpath('.//maxplaytime/@value')[0] if bool(item.xpath('.//maxplaytime/@value')) else None
        min_age = item.xpath('.//minage/@value')[0] if bool(item.xpath('.//minage/@value')) else None
        average_rating = item.xpath('.//statistics/ratings/average/@value')[0] if bool(item.xpath('.//statistics/ratings/average/@value')) else None
        bgg_rating = item.xpath('.//statistics/ratings/bayesaverage/@value')[0] if bool(item.xpath('.//statistics/ratings/bayesaverage/@value')) else None
        #rank = item.xpath('.//statistics/ratings/ranks/rank[@type="subtype"]/@value')[0] if bool(item.xpath('.//statistics/ratings/ranks/rank[@type="subtype"]/@value')) else None
        
        categories = []
        mechanics = []
        #publishers = []
        #designers = []
        #artists = []
        #expansions = []

        for category in item.xpath('.//link[@type="boardgamecategory"]'):
            categories.append(category.xpath('@value')[0])    
        categories = ", ".join(categories)

        for mechanic in item.xpath('.//link[@type="boardgamemechanic"]'):
            mechanics.append(mechanic.xpath('@value')[0])
        mechanics = ", ".join(mechanics)

        #for publisher in item.xpath('.//link[@type="boardgamepublisher"]'):
        #    publishers.append(publisher.xpath('@value')[0])    
        #publishers = ", ".join(publishers)

        #for designer in item.xpath('.//link[@type="boardgamedesigner"]'):
        #    designers.append(designer.xpath('@value')[0])    
        #designers = ", ".join(designers)

        #for artist in item.xpath('.//link[@type="boardgameartist"]'):
        #    artists.append(artist.xpath('@value')[0])    
        #artists = ", ".join(artists)

        #for expansion in item.xpath('.//link[@type="boardgameexpansion"]'):
        #    expansion_id = expansion.xpath('@id')[0]
        #    expansion_name = expansion.xpath('@value')[0]
        #    expansion_combo = expansion_id + "__" + expansion_name
        #    expansions.append(expansion_combo)    
        #expansions = ", ".join(expansions)
        
        game_info.append({
            'id':id,
            'name':name, 
            'image':image,
            #'thumbnail':thumbnail,
            'description':description,
            'min_players':min_players, 
            'max_players':max_players,
            #'playing_time':playing_time,
            'year_published':year_published,    
            'bgg_rating':bgg_rating,
            'avg_rating':average_rating, 
            #'rank':rank, 
            'categories':categories,
            'mechanics':mechanics,
            #'designers':designers,
            #'artists':artists,
            #'publishers':publishers,
            'min_playtime':min_playtime,
            'max_playtime':max_playtime,
            'min_age':min_age,
            })
        
    return game_info
