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
    # Show a list of games
    games = [game for game in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, game))]
    return render_template('index.html', games = games)

@app.route('/newgame/', methods = ['GET', 'POST'])
def new_game():
    # Allow the user to create a new game
    return '<em>TODO: Create a new game.</em>'

@app.route('/games/')
def games_index(game_path = None):
    # Redirect to the home page
    return redirect(url_for('index'))

@app.route('/games/<game>/')
def game_info(game):
    return '<em>TODO: Show game info for: %s</em>' % game

@app.route('/games/<game>/play/')
@app.route('/games/<game>/play/<path:data_path>', methods=['GET', 'POST'])
def game_player(game, data_path = None):
    # Reroute to Impact/game or abort if trying to access a file at Impact root
    if data_path and not os.path.dirname(data_path):
        abort(404)
    return handle_impactjs(data_path or 'index.html', game)

@app.route('/games/<game>/edit/')
@app.route('/games/<game>/edit/<path:data_path>', methods=['GET', 'POST'])
def game_editor(game, data_path = None):
    # Reroute to Impact/game or abort if trying to access a file at Impact root
    if data_path and not os.path.dirname(data_path):
        abort(404)
    return handle_impactjs(data_path or 'weltmeister.html', game)

@app.route('/impact/')
@app.route('/impact/<path:impact_url>', methods=['GET', 'POST'])
def handle_impactjs(impact_url = 'index.html', game = None):
    # Abort if there's no file to be retrieved
    if not os.path.basename(impact_url):
        abort(404)
    
    # Override the API
    if impact_url.startswith(IMPACT_API_URL):
        method = impact_url[len(IMPACT_API_URL):]
        def norm_url(url):
            if url.startswith('//'):
                abort(404)
            return url[1:] if url.startswith('/') else url
        def reroute_url(url):
            return url[len(IMPACT_GAME_URL):] if game and url.startswith(IMPACT_GAME_URL) else url
        def get_path(url, rerouted = True):
            return os.path.normpath(os.path.join(GAMES_DIR if game and rerouted else IMPACT_DIR, url)).replace('..', '')
        current_game_dir = os.path.join(GAMES_DIR, game) if game else IMPACT_DIR
        if method == 'glob.php':
            # TODO: Handle arrays of 'glob' URL arguments
            pattern = reroute_url(norm_url(request.args.get('glob[]', '')))
            path = get_path(pattern)
            print; print 'glob(%s) ->' % repr(str(pattern))
            # TODO: Really need to join with 'lib' here?
            files = [f[len(os.path.join(IMPACT_DIR, 'lib') + os.sep):] for f in glob.glob(path)]
            print '  ' + '\n  '.join(files) if len(files) > 0 else '  None'
            return json.dumps(files)
        elif method == 'browse.php':
            directory = norm_url(request.args.get('dir', ''))
            types = request.args.get('type')
            print; print 'browse(%s, %s) ->' % (repr(str(directory)), repr(str(types)))
            parent = os.path.dirname(directory) if directory else False
            path = os.path.normpath(os.path.join(current_game_dir, directory)).replace('..', '')
            exts = SUPPORTED_EXTENSIONS.get(types) or ['*.*']
            # Get the directories and files of the provided path, removing the base of the path (which leaves only the relative URL)
            dirs = [(directory + '/' + dirname) for dirname in os.listdir(path) if os.path.isdir(os.path.join(path, dirname))]
            files = []
            for ext in exts:
                files += [filename[len(current_game_dir):] for filename in glob.glob(os.path.join(path, ext))]
            print '  ' + '\n  '.join(files) if len(files) > 0 else '  None'
            return json.dumps({'dirs': dirs, 'files': files, 'parent': parent})
        elif method == 'save.php' and request.method == 'POST':
            path = request.form.get('path', '').replace('..', '').replace('\\', '/')
            data = request.form.get('data')
            if not path or not data:
                print '*** Save error: No data or path specified.'
                return json.dumps({'error': '1', 'msg': 'No Data or Path specified'})
            elif not path.endswith('.js'):
                print '*** Save error: File must have a .js extension.'
                return json.dumps({'error': '3', 'msg': 'File must have a .js suffix'})
            print 'Saving:', path
            print game
            # Reroute the path to the current game's level directory
            if game and path.startswith(IMPACT_GAME_URL):
                # TODO: How to handle the path?
                path = os.path.join(GAMES_DIR, game, path[len(IMPACT_GAME_URL):])
            path = os.path.normpath(os.path.join(IMPACT_DIR, path)).replace('..', '')
            # Write to file
            try:
                with open(path, 'w') as f:
                    f.write(data)
                return json.dumps({'error': 0})
            except:
                print '*** Save error: Could not write to file.'
                return json.dumps({'error': '2', 'msg': "Couldn't write to file: " + path})
        else:
            abort(404)
    
    # Reroute path, if current game exists, and use the local impact path otherwise
    if game and impact_url.startswith(IMPACT_GAME_URL):
        local_path = os.path.normpath(os.path.join(GAMES_DIR, game, impact_url[len(IMPACT_GAME_URL):]))
    elif game and impact_url.startswith(IMPACT_MEDIA_PATH):
        local_path = os.path.normpath(os.path.join(GAMES_DIR, game, impact_url))
    else:
        local_path = os.path.normpath(os.path.join(IMPACT_DIR, impact_url))
    
    # Abort if no impact file exists
    if not os.path.exists(local_path):
        abort(404)
    
    # Return the local file
    return send_file(local_path)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

# Run dev server
if __name__ == '__main__':
    app.run('localhost', port = 80, debug = True)
