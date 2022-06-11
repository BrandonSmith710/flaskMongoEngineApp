# flaskMongoEngineApp
This repository features a MongoDB database interface, which was built using the flask-mongoengine ODM, and allows you to load a csv file of billionaires into a database, then query the documents by net worth or country of citizenship. You can also perform a breadth first search on documents, which uses a graph structure to find all documents which are connected to the query document through any number of connections. Additionally delete documents or the entire collection, delete or create connections between documents, view all names in the database, and see first level connections of any specified document.

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
