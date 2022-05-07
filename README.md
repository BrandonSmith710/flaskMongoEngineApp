# flaskMongoEngineApi
This repository is a flask-mongoengine database and api, which allows you to load a csv file of billionaires into a MongoDB database, then query the documents by net worth or country of citizenship. You can also optionally delete the entire collection.

Installation Instructions

1) create database through mongodb
2) clone repository
3) python -m venv env
4) . env/Scripts/activate (Windows 10)
5) pip install -r requirements.txt
6) create .env
7) store auth. info inside .env
8) format database URI
9) export FLASK_APP=inner
10) flask run
