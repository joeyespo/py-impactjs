#!/usr/bin/env python

"""
Impactjs Backend Server
By Joe Esposito

Implements a back-end server in Python for impactjs. This server also manages
your games without any external dependencies or additional file manipulation.
"""

import os
import codecs, json
from flask import Flask, request, render_template, url_for, abort

# Constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMPACT_DIR = os.path.join(ROOT_DIR, 'impact')

# Functions
def static(filename):
    """Provides the 'static' function that also appends the file's timestamp to the URL, usable in a template."""
    url = url_for('.static', filename=filename)
    fname = os.path.join(os.path.join(app.root_path, 'static'), filename)
    st = int(os.path.getmtime(fname))
    url += '?' + str(st)
    return url

def get_impact_file(filename):
    """Gets the specified impact file, or the 404 page if it cannot be found."""
    if '..' in filename or filename.startswith('/'):
        abort(404)
    path = os.path.join(IMPACT_DIR, filename)
    try:
        with codecs.open(path,'r','utf-8') as impact_file:
            return impact_file.read()
    except IOError:
        return abort(404)

# Flask application
app = Flask(__name__)
app.jinja_env.globals.update(static=static)

# Views
@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/new/')
def play(game_name = None):
    return '<em>TODO: Create a new game.</em>'

@app.route('/play/')
@app.route('/play/<game_name>')
def play(game_name = None):
    return '<em>TODO: Add a redirect to playing the selected game.</em>'

@app.route('/edit/')
@app.route('/edit/<game_name>')
def edit(game_name = None):
    return '<em>TODO: Add a redirect to editing the selected game.</em>'

@app.route('/impact/')
@app.route('/impact/<path:impact_path>')
def impact_file(impact_path = ''):
    if not os.path.basename(impact_path):
        impact_path = os.path.join(impact_path, 'index.html')
    return get_impact_file(impact_path)

# Override the Impact API
@app.route('/impact/lib/weltmeister/api/glob.php')
def impact_api(**args):
    # TODO: Redirect 'game' to the current game (if any)
    globs = request.args.get('glob[]', '')
    if not globs:
        return json.dump([])
    globs = os.path.join(IMPACT_DIR, globs)
    path, ext = os.path.split(globs)
    files = os.listdir(path) if ext.startswith('*') else [globs]
    return json.dumps(files)

@app.route('/impact/lib/weltmeister/api/browse.php')
def impact_api(**args):
    # TODO: Redirect 'game' to the current game (if any)
    return json.dumps([])
    

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error404.html'), 404

# Run dev server
if __name__ == '__main__':
    app.run('localhost', port=80, debug=True)
