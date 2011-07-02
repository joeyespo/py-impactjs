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
API_PATH = 'lib/weltmeister/api/'

# Flask application
app = Flask(__name__)

# Views
@app.route('/')
def index():
    games = [game for game in os.listdir(GAMES_DIR) if os.path.isdir(os.path.join(GAMES_DIR, game))]
    return render_template('index.html', games = games)

@app.route('/new/')
def new_game(game_name = None):
    return '<em>TODO: Create a new game.</em>'

@app.route('/games/')
def games_index(game_path = None):
    return redirect(url_for('index'))

@app.route('/games/<path:game_path>')
def play_game(game_path = None):
    game, action = os.path.split(os.path.normpath(game_path))
    if os.path.split(game)[0] or (action and action != 'edit'):
        abort(404)
    return handle_impactjs('weltmeister.html' if action else 'index.html', game)

@app.route('/impact/')
@app.route('/impact/<path:impact_path>', methods=['GET', 'POST'])
def handle_impactjs(impact_path = 'index.html', game = None):
    # Method to reroute the game URLs
    def reroute(path):
        if game:
            # TODO: implement
            pass
        return path
    
    # Override the API
    if impact_path.startswith(API_PATH):
        method = impact_path[len(API_PATH):]
        if method == 'glob.php':
            # TODO: Handle arrays of 'glob' URL arguments
            path = os.path.normpath(os.path.join(IMPACT_DIR, request.args.get('glob[]', ''))).replace('..', '')
            # TODO: Really need to join with 'lib' here?
            files = [f[len(os.path.join(IMPACT_DIR, 'lib') + os.sep):] for f in glob.glob(path)]
            return json.dumps(files)
        elif method == 'browse.php':
            path = os.path.normpath(os.path.join(IMPACT_DIR, request.args.get('dir', ''))).replace('..', '')
            exts = SUPPORTED_EXTENSIONS.get(request.args.get('type')) or ['*.*']
            # Get the directories and files of the provided path, removing the base of the path (which leaves only the relative URL)
            dirs = [dirname[len(IMPACT_DIR):] for dirname in os.listdir(path) if os.path.isdir(os.path.join(path, dirname))]
            files = []
            for ext in exts:
                files += [filename[len(IMPACT_DIR):] for filename in glob.glob(os.path.join(path, ext))]
            return json.dumps({'dirs': dirs, 'files': files, 'parent': path == IMPACT_DIR})
        elif method == 'save.php' and request.method == 'POST':
            # TODO: implement
            path = request.args.get('path')
            data = request.args.get('data')
            if not path or not data:
                return {'error': '1', 'msg': 'No Data or Path specified'}
            elif not path.endswith('.js'):
                return {'error': '3', 'msg': 'File must have a .js suffix'}
            path = os.path.normpath(os.path.join(IMPACT_DIR, path)).replace('..', '')
            # Write to file
            try:
                with open(path, 'w') as f:
                    f.write(data)
                return {'error': 0}
            except:
                return {'error': '2', 'msg': "Couldn't write to file: " + path}
        else:
            abort(404)
    
    # Get the local path and send back the specified file
    path = os.path.normpath(os.path.join(IMPACT_DIR, impact_path))
    print
    print ' ', path
    
    return send_file(path)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

# Run dev server
if __name__ == '__main__':
    app.run('localhost', port=80, debug=True)
