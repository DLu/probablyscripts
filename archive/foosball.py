#!/usr/bin/python
import requests  # pip install requests
import collections
import tempfile
import subprocess


class Player:

    def __init__(self):
        self.wins = 0
        self.losses = 0

    def __repr__(self):
        return "%d\t%d\t%d\t%.3f" % (
            self.wins, self.losses, self.wins + self.losses, float(self.wins) / (self.wins + self.losses))


def read_games():
    games = []
    response = requests.get(
        'https://docs.google.com/spreadsheet/ccc?key=0ArCi1BfUMYrzdFhGdzc5NUJzS0xxX281QmF1RVJ4dmc&output=csv')
    for line in response.content.split('\n')[1:]:
        games.append(line.split(','))
    return games

games = read_games()
#games = [('11/2/2012 14:55:28', 'DLu/AKargol', 'KMiskell/CMurdock', '7')]
players = collections.defaultdict(Player)

for game in games:
    for winner in game[1].split('/'):
        players[winner].wins += 1
    for loser in game[2].split('/'):
        players[loser].losses += 1
s = '<script src="sorttable.js"></script><table class="sortable"><thead><tr><th>Player<th>Wins<th>Losses<th>Games<th>Win%</thead><tbody> '
for n, p in sorted(players.items(), key=lambda p: p[1].wins, reverse=True):
    s += "<tr align=\"center\"><td>%s<td>%d<td>%d<td>%d<td>%.3f" % (
        n, p.wins, p.losses, p.wins + p.losses, float(p.wins) / (p.wins + p.losses))

s += '</table>'
import datetime
s += '<p style="font-size: small">Click column heading to sort</p>'
s += "<p><b>Last Updated:</b> %s" % str(datetime.datetime.now())[:-10]
f = tempfile.NamedTemporaryFile()
f.write("""<head>
<link href='http://fonts.googleapis.com/css?family=Autour+One' rel='stylesheet' type='text/css'>
</head>
<body style="font-family: 'Autour One', cursive;">
<table cellpadding="10">
<tr><td valign="top">
<h1>M&M Foosball Stats</h1>
<a href="https://docs.google.com/spreadsheet/ccc?key=0ArCi1BfUMYrzdFhGdzc5NUJzS0xxX281QmF1RVJ4dmc">Full Game Log</a><br />""")
f.write(s)
f.write("""<td><iframe src="https://docs.google.com/spreadsheet/embeddedform?formkey=dFhGdzc5NUJzS0xxX281QmF1RVJ4dmc6MQ" width="300" height="600" frameborder="0" marginheight="0" marginwidth="0">Loading...</iframe>
</table></body>""")
f.flush()
subprocess.call(
    ['scp', f.name, 'dvl1@ssh.seas.wustl.edu:/home/research/dvl1/public_html/foosball/index.html'])
f.close()
