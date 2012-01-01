from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import *
from django.utils import simplejson
import csv
from models import Team
import urllib2
import re
import boxscore
from django.template import Context,Template
from django.template import loader
import os.path
import base64
import urllib
from HTMLParser import HTMLParser

def unescape_html(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s
	
def get_teams():
    reader = csv.reader(open(os.path.abspath("static/teams.txt"), "rb"));
    teams = []
    for row in reader:
        teams.append({'abbr': row[0], 'name': row[2]})
    return teams

def preview(request):
    html = unescape_html(base64.b64decode(request.GET['html']))
    print html
    return render_to_response('preview.html', {'html': html})

def home(request):
    return render_to_response('home.html', {'teams': get_teams()})

def lines(request):
    abbr = request.POST['abbr']
    name = request.POST['name']
    box = boxscore.get_boxscore(abbr, name)
    template = loader.get_template('linesform.html')
    html = template.render(Context({"starters": box[0], "bench": box[1]}))
    return HttpResponse(simplejson.dumps({'html': html}), mimetype='application/javascript')
 
 
 
def decorate_lines(request, lines):
    temp = []
    for l in lines:
        blurb = request.POST['player_blurb_' + str(l['id'])]
        if blurb != '':
            temp.append(l)

    for l in temp:
        l['blurb'] = request.POST['player_blurb_' + str(l['id'])]
        l['rating'] = request.POST['player_rating_' + str(l['id'])]
        l['image'] = "http://a.espncdn.com/combiner/i?img=/i/headshots/nba/players/full/" + str(l['id']) + ".png&w=65&h=90&scale=crop&background=0xffffff&transparent=false"
    
    return temp

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

    # list of things
    things = []
    for t in request.POST.getlist('things'):
        if t != '':
	    things.append(t) 
    # create html
    template = loader.get_template('reaction.html')
    html = template.render(Context({"starters": starters, "bench": bench, 'game_id': game_id, 'abbrs': abbrs, 'names': names, 'score': score, 'things': things}))
    
    # create css
    f = urllib2.urlopen('http://saltcityhoops.com/thn-recaps/thn-styles.css')
    css = f.read()

    # css and html combined into one payload to be returned to browser
    template = loader.get_template('markup.html')
    full_markup = template.render(Context({"css": css, "html": html, "payload_encoded": urllib.urlencode({'html': base64.b64encode(html)})  }))
    return HttpResponse(simplejson.dumps({'html': full_markup}), mimetype='application/javascript')
    
