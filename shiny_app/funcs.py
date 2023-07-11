import requests
from lxml import etree
import re

def retrieve_game_info(game_ids):

    id_list = ','.join(str(game_id) for game_id in game_ids)
    url = f'https://boardgamegeek.com/xmlapi2/thing?id={id_list}&stats=1'
    response = requests.get(url)
    return response.content, response.text # Change when done debugging

def parse_bgg_xml(xml_data):
    
    game_info = []
    
    root = etree.fromstring(xml_data)

    for item in root.xpath('//item'):
        game_name = item.xpath('.//name[@type="primary"]/@value')[0]
        thumbnail = item.xpath('thumbnail/text()')[0]
        image = item.xpath('image/text()')[0]
        description = item.xpath('description/text()')[0]
        year_published = item.xpath('.//yearpublished/@value')[0]
        min_players = item.xpath('.//minplayers/@value')[0]
        max_players = item.xpath('.//maxplayers/@value')[0]
        playing_time = item.xpath('.//playingtime/@value')[0]
        min_playtime = item.xpath('.//minplaytime/@value')[0]
        max_playtime = item.xpath('.//maxplaytime/@value')[0]
        min_age = item.xpath('.//minage/@value')[0]
        average_rating = item.xpath('.//statistics/ratings/average/@value')[0]
        bgg_rating = item.xpath('.//statistics/ratings/bayesaverage/@value')[0]
        
        description=re.sub(r"(&#10;)+", " ", description)
        description=re.sub(r"(&quot;)", '"', description)
        
        game_info.append({
            'game_name':game_name, 
            'thumbnail':thumbnail,
            'image':image,
            'description':description,
            'year_published':year_published, 
            'min_players':min_players, 
            'max_players':max_players,
            'playing_time':playing_time,
            'min_playtime':min_playtime,
            'max_playtime':max_playtime,
            'min_age':min_age,
            'average_rating':average_rating, 
            'bgg_rating':bgg_rating
            })
        
    return game_info