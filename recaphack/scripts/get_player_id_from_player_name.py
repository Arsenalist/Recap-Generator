from bs4 import BeautifulSoup
import requests

def get_player_id(link):
    r = requests.get(link)
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text)
    stats_tab = soup.select('#tab-stats')
    return stats_tab[0]['href'].split('=')[1]


r = requests.get('http://stats.nba.com/players.html')
soup = BeautifulSoup(r.text)
players = soup.find(id='active-players').find_all('a', class_='playerlink')
contents = ""
for p in players:
    name = p.string
    if "," in name:
        name = name.string.split(',')    
        name = name[1].strip() + ' ' + name[0].strip()
    player_id = get_player_id(p['href'])
    if player_id is not None:
        print name + "=" + get_player_id(p['href'])
        if name == "Charles Hayes":
            print "Chuck Hayes=" + get_player_id(p['href'])


