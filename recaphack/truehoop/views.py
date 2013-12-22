from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import *
from django.utils import simplejson
import csv
from models import Recap
import urllib2
import re
import boxscore
from django.template import Context,Template
from django.template import loader
import os.path
import urllib


def unescape_html(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
	
def get_teams():   
    location = "/www/Recap-Generator/recaphack/static/teams.txt"
    reader = csv.reader(open(location, "rb"))
    teams = []
    for row in reader:
        teams.append({'abbr': row[0], 'name': row[2]})
    return teams

def preview(request):
    recap = Recap.objects.get(pk=request.GET['id'])
    return render_to_response('preview.html', {'html': recap.html, 'css': recap.css})

def home(request):
    return render_to_response('home.html', {'teams': get_teams()})

def lines(request):
    abbr = request.POST['abbr']
    name = request.POST['name']    
    coach_info = boxscore.get_coach_info(abbr)
    box = boxscore.get_boxscore(abbr, name)
    template = loader.get_template('linesform.html')
    html = template.render(Context({"starters": box[0], "bench": box[1], "coach": coach_info}))
    return HttpResponse(simplejson.dumps({'html': html}), mimetype='application/javascript')
 
def decorate_lines(request, lines):
    temp = []
    for l in lines:
        key = 'player_blurb_' + str(l['id'])
	if key in request.POST.keys():
	    blurb = request.POST[key]
	    if blurb != '':
                temp.append(l)

    for l in temp:
        l['blurb'] = request.POST['player_blurb_' + str(l['id'])]
        l['rating'] = request.POST['player_rating_' + str(l['id'])]
        if l['rating'] == 'inc':
            l['rating'] = 'http://i3.minus.com/ibyI6HKMAr5o6L.jpg'
        else:
            l['rating'] = 'http://espn.go.com/i/nfl/grades/grade_' + l['rating'] + '.jpg'
            l['image'] = boxscore.get_player_image(l['id']) 
    return temp

def add_nba_data(starters, abbr):
    import ConfigParser
    team_config = ConfigParser.ConfigParser()
    team_config.read('/www/Recap-Generator/recaphack/static/nba.com.teams.txt')
    nba_team_id = team_config.get('Teams', abbr)
    nba_game_id = get_latest_nba_com_game_id(nba_team_id)

    player_config = ConfigParser.ConfigParser()
    player_config.read('/www/Recap-Generator/recaphack/static/nba.com.players.txt')
    for s in starters:
        name_without_position = s['Name'].split(',')[0]    
        nba_player_id = player_config.get('ActivePlayers', name_without_position)
        if nba_player_id is None:
            continue
        shot_chart_link = '<a class="shot-chart" href="http://stats.nba.com/shotchartPopup.html?Season=2013-14&TeamID=' + str(nba_team_id) + '&PlayerID=' + str(nba_player_id) + '&GameID=' + str(nba_game_id)  + '&ContextMeasure=FG_PCT">Shot Chart</a>'
        s['Name'] = s['Name'] + " " + shot_chart_link
    return starters

def get_latest_nba_com_game_id(nba_team_id):
    from subprocess import check_output
    latest_game_id = check_output(["get_latest_game_id_from_team_id", nba_team_id]).strip()
    return latest_game_id


def markup(request):
    abbr = request.POST['abbr']
    name = request.POST['name']
    box = boxscore.get_boxscore(abbr, name)
    starters = box[0]
    bench = box[1]
    game_id = box[2]
    abbrs = box[3]
    names = box[4]
    score = box[5]
    starters = decorate_lines(request, starters)
    bench = decorate_lines(request, bench)
    if 'show_nba_data' in request.POST:
        starters = add_nba_data(starters, abbr)
        bench = add_nba_data(bench, abbr)
    coach = {'name': request.POST['coach_name'], 'image': request.POST['coach_image'], 'blurb': request.POST['coach_blurb'], 'rating': request.POST['coach_rating']}

    allow_user_voting = 'allow_user_voting' in request.POST
    # utah workaoround
    #if abbrs[0] == 'utah':
    #    abbrs[0] = 'uta'

    #if abbrs[1] == 'utah':
    #    abbrs[1] = 'uta'

    # list of things
    things = []
    for t in request.POST.getlist('things'):
        if t != '':
	    things.append(t) 
    num_names = ['One Thing', 'Two Things', 'Three Things', 'Four Things', 'Five Things']
    str_things_count = None
    if things:
        str_things_count = num_names[len(things)-1]
    # create html
    template = loader.get_template('reaction.html')
    html = template.render(Context({"allow_user_voting": allow_user_voting, "team_id": abbr, "starters": starters, "bench": bench, 'game_id': game_id, 'abbrs': abbrs, 'names': names, 'score': score, 'things': things, 'str_things_count': str_things_count, 'coach': coach}))
    
    # create css

    location = "/www/Recap-Generator/recaphack/static/styles.css"
    f = open(location, "r")
    css = f.read()

    r = Recap(html=html, css=css, home_abbr=abbrs[1], away_abbr=abbrs[0], home_name=names[1], away_name=names[0], home_score=score[1], away_score=score[0])
    home_abbr = abbrs[1]
    r.save()
    # css and html combined into one payload to be returned to browser
    template = loader.get_template('markup.html')
    full_markup = template.render(Context({"css": css, "html": html, "id": r.id }))
    return HttpResponse(simplejson.dumps({'html': full_markup}), mimetype='application/javascript')
    
