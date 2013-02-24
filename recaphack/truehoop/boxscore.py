import urllib2
import re
from xml.dom.minidom import parse, parseString
from pyquery import PyQuery as pq
from lxml import etree


def get_coach_info(abbr):    
    f = urllib2.urlopen('http://espn.go.com/nba/team/roster/_/name/' + abbr)
    contents  = f.read()
    d = pq(contents)
    # get name and url of coach page    
    name = d('.total td a').text()
    url = d('.total td a').attr('href')

    # from url of coach name, get coach image
    f = urllib2.urlopen(url)
    contents  = f.read()
    d = pq(contents)
    image = d('table.tablehead tr:nth-child(2) td img').attr('src')
    return (name, image)
 


    

def get_latest_game_id(abbr):
    # get last game id by scanning schedule page
    f = urllib2.urlopen('http://espn.go.com/nba/team/_/name/' + abbr)
    contents  = f.read().replace('\n', '')
    matches  = re.findall(r'/nba/boxscore\?id=(\d+)', contents)
    return int(matches[-1])

def get_page_html(id):
    f = urllib2.urlopen('http://espn.go.com/nba/boxscore?id=' + str(id))
    return f.read().replace('\n', '')
 
def get_boxscore_dom(page_html):
    r = re.findall(r'<table border="0" width="100%" class="mod-data">.*</table>', page_html)
    table = r[-1]
    table = re.sub(r'(<tr\s(.*?)>)','<tr>', table)
    table = re.sub(r'(<td\s(.*?)>)','<td>', table)
    table = re.sub(r'(width=\d+%|nowrap|&nbsp;)','', table).replace('OREB</td>', 'OREB</th>')
    table = '<?xml version="1.0" encoding="Latin-1"?>' + table
    print table
    return parseString(table)
   

def get_location(dom, team):
    ths =  dom.getElementsByTagName('th');
    i = 0
    for th in ths:
        nodes = th.childNodes        
        for n in nodes:
            if n.nodeType == n.TEXT_NODE:
               if i == 2 and team in n.data:
                    return 'away'
               if i == 48 and team in n.data:
                    return 'home'
            i = i + 1
    return None


def get_group_lines(dom, tbody_index):
    line_headers = ['Name', 'min', 'FG', '3FG', 'FT', 'OREB', 'DREB', 'reb', 'ast', 'stl', 'blk', 'to', 'pf', 'plusminus', 'pts']
    tbodies = dom.getElementsByTagName('tbody');
    i = 0
    lines = []
    for tbody in tbodies:
        if i == tbody_index:
           trs = tbody.childNodes        
           for tr in trs:
             tds = tr.childNodes
             line = {}
             td_index = 0
             for td in tds:
                 nodes = td.childNodes
                 for n in nodes:
                     if n.nodeType == n.TEXT_NODE:
                         if td_index == 0:
                             line[line_headers[td_index]] = line[line_headers[td_index]] + n.data
                         else:
                             line[line_headers[td_index]] = n.data
                     else:
                         line[line_headers[td_index]] = n.childNodes[0].data
                         profile_url = n.attributes.getNamedItem('href').nodeValue
                         matches  = re.findall(r'/id/(\d+)/', profile_url)
                         line['id'] = int(matches[-1])
                 td_index = td_index + 1
             lines.append(line)
        i = i + 1
    return lines



def get_all_lines(dom, team):
    location = get_location(dom, team)
    if location == None:
        print "Location could not be determined"
    starters_tbody = None
    bench_tbody = None
    if location == 'home':
        starters_tbody = 3
        bench_tbody = 4
    elif location == 'away':
        starters_tbody = 0
        bench_tbody = 1

    starters = get_group_lines(dom, starters_tbody)
    bench = get_group_lines(dom, bench_tbody)
    return [starters, bench]

def get_team_abbrs(page_html, game_id):
    matches = re.findall(r"espn:nba:game:boxscore:" + str(game_id) + "\+-\+(\w+)\+at\+(\w+)", page_html)
    return list(matches[-1])


def get_team_names(page_html):
    matches = re.findall(r"<title>(.*?)\svs\.\s(.*?)\s-", page_html)
    return list(matches[-1])

def get_final_score(dom):
    tbodies = dom.getElementsByTagName('tbody')
    away = tbodies[2].childNodes[0].childNodes[13].childNodes[0].childNodes[0].data
    home = tbodies[5].childNodes[0].childNodes[13].childNodes[0].childNodes[0].data
    return [away, home]

def get_boxscore(abbr, name):
    latest_game_id = get_latest_game_id(abbr)
    page_html = get_page_html(latest_game_id)
    dom = get_boxscore_dom(page_html)
    lines = get_all_lines(dom, name)
    lines.append(latest_game_id)
    lines.append(get_team_abbrs(page_html, latest_game_id))
    lines.append(get_team_names(page_html))
    lines.append(get_final_score(dom))
    return lines

