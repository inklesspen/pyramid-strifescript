strifescript README
==================

This is a webapp designed to handle Burning Wheel and Mouse Guard's
conflict resolution scheme. It has an unusual system for a RPG;
players have to choose three successive actions, lock them in, and
then reveal them one at a time. Simple at the table, yet hard online.

This was my second attempt at writing a solution, during the spring of
2013. The server setup worked pretty well, but I made some mistakes
with the rich-JS-app frontend, so I'm fixing that.


Getting Started
---------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/initialize_strifescript_db development.ini

- $venv/bin/pserve development.ini

