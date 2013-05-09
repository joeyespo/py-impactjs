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
VERBOSE = False
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
    if page in ['index.html', 'weltmeister.html'] and not is_impact_installed():
        return render_template('impact-not-installed.html')
    try:
        return send_game_file(game,page)
    except IOError as e:
        try:
            return send_impact_file(page)
        except IOError:
            abort(404)

@app.route('/games/<game>/tools/<path:subpath>')
def get_tool(game, subpath):
    try:
        return send_impact_file('tools', subpath)
    except IOError:
        abort(404)

@app.route('/games/<game>/media/<path:subpath>')
def get_media(game, subpath):
    try:
        return send_game_file(game, 'media', subpath)
    except IOError:
        abort(404)

@app.route('/games/<game>/lib/<path:subpath>')
def get_impact_file(game, subpath):
    try:
        return send_impact_file('lib', subpath)
    except IOError:
        abort(404)

@app.route('/games/<game>/lib/game/<path:subpath>')
def get_game_file(game, subpath):
    try:
        return send_game_file(game, 'lib', 'game', subpath)
    except IOError:
        abort(404)

@app.route('/games/<game>/lib/weltmeister/api/glob.php')
def glob_api_override(game):
    # TODO: Handle arrays of 'glob' URL arguments
    pattern = norm_path(request.args.get('glob[]', ''))
    pattern_dir = os.path.dirname(pattern) + '/'
    if VERBOSE: print; print 'glob(%s) ->' % repr(str(pattern))
    local_path = os.path.join(GAMES_DIR, game, os.path.normpath(pattern))
    files = [(pattern_dir + os.path.basename(f)) for f in glob.glob(local_path)]
    if VERBOSE: print '  ' + '\n  '.join(files) if len(files) > 0 else '  None'
    return json.dumps(files)

@app.route('/games/<game>/lib/weltmeister/api/browse.php')
def browse_api_override(game):
    directory = norm_path(request.args.get('dir', ''))
    types = request.args.get('type')
    parent = os.path.dirname(directory) if directory else False
    exts = SUPPORTED_EXTENSIONS.get(types) or ['*.*']
    if VERBOSE: print; print 'browse(%s, %s) ->' % (repr(str(directory)), repr(str(types)))
    local_path = os.path.join(GAMES_DIR, game, os.path.normpath(directory))
    directory += '/' if directory else ''
    # Get the directories and files of the provided path, removing the base of the path (which leaves only the relative URL)
    dirs = [(directory + dirname) for dirname in os.listdir(local_path) if os.path.isdir(os.path.join(local_path, dirname))]
    files = []
    for ext in exts:
        files += [directory + os.path.basename(filename) for filename in glob.glob(os.path.join(local_path, ext))]
    items = dirs + files
    if VERBOSE: print '  ' + '\n  '.join(items) if len(items) > 0 else '  None'
    return json.dumps({'dirs': dirs, 'files': files, 'parent': parent})

@app.route('/games/<game>/lib/weltmeister/api/save.php', methods=['POST'])
def save_api_override(game):
    path = norm_path(request.form.get('path', ''))
    data = request.form.get('data')
    if VERBOSE: print; print 'saving(%s) ->' % path
    if not path or not data:
        if VERBOSE: print '*** Save error: No data or path specified.'
        return json.dumps({'error': '1', 'msg': 'No Data or Path specified'})
    elif not path.endswith('.js'):
        if VERBOSE: print '*** Save error: File must have a .js extension.'
        return json.dumps({'error': '3', 'msg': 'File must have a .js suffix'})
    local_path = os.path.join(GAMES_DIR, game, path)
    # Write to file
    try:
        with open(local_path, 'w') as f:
            f.write(data)
        return json.dumps({'error': 0})
    except:
        if VERBOSE: print '*** Save error: Could not write to file.'
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

def is_impact_installed():
    return os.path.exists(os.path.join(IMPACT_DIR, 'index.html')) and os.path.exists(os.path.join(IMPACT_DIR, 'weltmeister.html'))

def send_impact_file(*pathparts):
    """Sends a file by joining the specified path parts from the impact directory."""
    filename = os.path.join(IMPACT_DIR, *pathparts)
    if not os.path.exists(filename):
        raise IOError(5,'No impact file %s' % filename,filename)
    return send_file(filename)

def send_game_file(game, *pathparts):
    """Sends a file by joining the specified path parts from the current game directory."""
    filename = os.path.join(GAMES_DIR, game, *pathparts)
    if not os.path.exists(filename):
        raise IOError(5,'No game file %s' % filename,filename)
    return send_file(filename)

# Run dev server
if __name__ == '__main__':
    app.run('localhost', port = 80, debug = True)
