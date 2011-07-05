#!/usr/bin/env python

"""
Impactjs Backend Server
By Joe Esposito

Implements a back-end server in Python for Impact by handling the original API
originally implemented in PHP and allowing multiple games by re-routing URLs.
"""

import os, glob, codecs, json
from flask import Flask, abort, url_for, request, render_template, send_file, redirect

# Constants
SUPPORTED_EXTENSIONS = {'images': ['*.png', '*.gif', '*.jpg', '*.jpeg'], 'scripts': ['*.js']}
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'games'))
IMPACT_DIR = os.path.normpath(os.path.join(ROOT_DIR, 'impact')) + os.sep
IMPACT_MEDIA_PATH = 'media/'
IMPACT_GAME_URL = 'lib/game/'
IMPACT_API_URL = 'lib/weltmeister/api/'

# Flask application
app = Flask(__name__)

# Views
@app.route('/')
def index():
    games = [game for game in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, game))]
    return render_template('index.html', games = games)

@app.route('/games/')
def games_index():
    return redirect(url_for('index'))

@app.route('/games/<game>/overview.html')
def game_overview(game):
    return '<em>TODO: Show game info for: %s</em>' % game

@app.route('/games/<game>/')
@app.route('/games/<game>/<page>')
def play_game(game, page = 'index.html'):
    return send_impact_file(page)

@app.route('/games/<game>/tools/<path:subpath>')
def get_tool(game, subpath):
    return send_impact_file('tools', subpath)

@app.route('/games/<game>/media/<path:subpath>')
def get_media(game, subpath):
    return send_game_file(game, 'media', subpath)

@app.route('/games/<game>/lib/<path:subpath>')
def get_impact_file(game, subpath):
    return send_impact_file('lib', subpath)

@app.route('/games/<game>/lib/game/<path:subpath>')
def get_game_file(game, subpath):
    return send_game_file(game, 'lib', 'game', subpath)

@app.route('/games/<game>/lib/weltmeister/api/glob.php')
def glob_api_override(game):
    # TODO: Handle arrays of 'glob' URL arguments
    pattern = norm_path(request.args.get('glob[]', ''))
    pattern_dir = os.path.dirname(pattern) + '/'
    print; print 'glob(%s) ->' % repr(str(pattern))
    local_path = os.path.join(GAMES_DIR, game, os.path.normpath(pattern))
    files = [(pattern_dir + os.path.basename(f)) for f in glob.glob(local_path)]
    print '  ' + '\n  '.join(files) if len(files) > 0 else '  None'
    return json.dumps(files)

@app.route('/games/<game>/lib/weltmeister/api/browse.php')
def browse_api_override(game):
    directory = norm_path(request.args.get('dir', ''))
    types = request.args.get('type')
    parent = os.path.dirname(directory) if directory else False
    exts = SUPPORTED_EXTENSIONS.get(types) or ['*.*']
    print; print 'browse(%s, %s) ->' % (repr(str(directory)), repr(str(types)))
    local_path = os.path.join(GAMES_DIR, game, os.path.normpath(directory))
    directory += '/' if directory else ''
    # Get the directories and files of the provided path, removing the base of the path (which leaves only the relative URL)
    dirs = [(directory + dirname) for dirname in os.listdir(local_path) if os.path.isdir(os.path.join(local_path, dirname))]
    files = []
    for ext in exts:
        files += [directory + os.path.basename(filename) for filename in glob.glob(os.path.join(local_path, ext))]
    items = dirs + files
    print '  ' + '\n  '.join(items) if len(items) > 0 else '  None'
    return json.dumps({'dirs': dirs, 'files': files, 'parent': parent})

@app.route('/games/<game>/lib/weltmeister/api/save.php', methods=['POST'])
def save_api_override(game):
    path = norm_path(request.form.get('path', ''))
    data = request.form.get('data')
    print; print 'saving(%s) ->' % path
    if not path or not data:
        print '*** Save error: No data or path specified.'
        return json.dumps({'error': '1', 'msg': 'No Data or Path specified'})
    elif not path.endswith('.js'):
        print '*** Save error: File must have a .js extension.'
        return json.dumps({'error': '3', 'msg': 'File must have a .js suffix'})
    local_path = os.path.join(GAMES_DIR, game, path)
    # Write to file
    try:
        with open(local_path, 'w') as f:
            f.write(data)
        return json.dumps({'error': 0})
    except:
        print '*** Save error: Could not write to file.'
        return json.dumps({'error': '2', 'msg': "Couldn't write to file: " + path})

@app.route('/newgame', methods = ['GET', 'POST'])
def new_game():
    return '<em>TODO: Create a new game.</em>'

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

# Helper functions
def norm_path(remote_path):
    """Normalizes the specified remote path or return None if it is invalid."""
    remote_path = remote_path[1:] if remote_path.startswith('/') else remote_path
    if remote_path.endswith('/'):
        remote_path = remote_path[:-2]
    if remote_path.startswith('..') or os.path.isabs(remote_path):
        return None
    return remote_path
    
def get_local_path(remote_path, current_game = None):
    """Returns the local current game file if it exists, or the local impact file otherwise (or none if it does not exist)."""
    # Get the os-normalized path
    remote_path = os.path.normpath(remote_path)
    # Get the local game file and return it if it exists
    if current_game:
        local_game_path = os.path.join(GAMES_DIR, current_game, remote_path)
        if os.path.exists(local_game_path):
            return local_game_path
    # Get the local impact file and return it if it exists
    local_impact_path = os.path.join(IMPACT_DIR, remote_path)
    if os.path.exists(local_impact_path):
        return local_impact_path
    # Return None since no local file exists
    return None

def send_impact_file(*pathparts):
    """Sends a file by joining the specified path parts from the impact directory."""
    return send_file(os.path.join(IMPACT_DIR, *pathparts))

def send_game_file(game, *pathparts):
    """Sends a file by joining the specified path parts from the current game directory."""
    return send_file(os.path.join(GAMES_DIR, game, *pathparts))

# Run dev server
if __name__ == '__main__':
    app.run('localhost', port = 80, debug = True)
