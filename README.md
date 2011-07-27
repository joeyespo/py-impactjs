Py-Impactjs
===========

Implements a back-end server in Python for impactjs. This server also manages
your games without any external dependencies or additional file manipulation.

This allows you to:

* Work on multiple games without moving any directories around
* Add your games to source control without the risk of accidentally checking in the Impact lib (this works because you copy Impact into the 'impact' directory, while your games are located in the 'games' directory; the project wires it all together)
* Run a server from any directory, since there's no installation or predefined paths
* Bake and deploy with the click of an in-browser button
* Create new games and scaffolds from within the browser

Note that both the 'Impact' and 'games' directory are in .gitignore. This will keep any accidental checkins of your games and Impact to Py-Impactjs.

To start, copy your Impact library into the 'impact' directory and run py_impactjs.py.


Dependencies
------------

Python
