import mongoengine as me
from flask import Flask, redirect, render_template, request, url_for
from flask_mongoengine import MongoEngine
from .modelgorithm import Graph, Billionaire, breadthFirstSearch
import pandas as pd
import os
from dotenv import load_dotenv


def create_app():
    load_dotenv()
    DB_URI = f'''mongodb+srv://{os.getenv('USER')}:{
        os.getenv('PASSWORD')
        }@pythoncluster.gv91d.mongodb.net/{
        os.getenv('DB_NAME')}?retryWrites=true&w=majority'''

    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        'host': DB_URI,
        'authentication_source': 'admin'
    }
    db = MongoEngine(app)

    @app.route('/', methods = ['GET', 'POST'])
    def root():
        """This route requests two space separated integers,
           returned is a queryset of existing database
           objects whose net worth values fall in the
           specified range."""


        if request.method == 'POST':
            w = request.form.get('search').split()
            if all(arg.isdigit() for arg in w):
                if len(w) == 2:
                    worth_l, worth_u = int(w[0]), int(w[1])
                    try:
                        bills = Billionaire.objects(
                            worth__gte = worth_l,
                            worth__lte = worth_u,
                            )
                    except IndexError:
                        return redirect(url_for(''))
                    worths = set(bill.worth for bill in bills)
                    groups = {f'${worth}': [
                    bill.name for bill in bills if bill.worth == worth
                    ] for worth in worths
                    }
                    return render_template('results.html',
                                            answer = groups)
                return render_template('base.html')
            return render_template('base.html')
        return render_template('base.html')

    @app.route('/query_by_citizenship', methods = ['GET', 'POST'])
    def query_by_citizenship():
        """This route accepts a country name and returns
           all billionaire objects with a citizenship
           value equal to the input country."""


        if request.method == 'POST':
            w = request.form.get('search1')
            try:
                bills = Billionaire.objects(citizenship__iwholeword = w)
                answer = f'''Billionaires with citizenship in {
                    bills[0].citizenship}: ''' + ', '.join(
                    f'''{bill.name} is worth ${bill.worth
                    }''' for bill in bills
                    )
                return render_template('results1.html', answer = answer)
            except IndexError:
                return redirect(url_for('query_by_citizenship'))
        return render_template('base1.html')

    @app.route('/add_user', methods = ['POST', 'GET'])
    def add_user():
        '''This route requests constructor variables and
           then creates a new object in the database,
           connections must be added through the add_friend
           route currently.'''


        if request.method == 'POST':
            name = request.form.get('search1_1')
            age = request.form.get('search1_2')
            worth = request.form.get('search1_3')
            category = request.form.get('search1_4')
            citizenship = request.form.get('search1_5')
            gender = request.form.get('search1_6')
            try:
                b = Billionaire.objects(name = name)[0]
                answer = f'{b.name} is an existing user'
            except IndexError:
                id = len(Billionaire.objects())
                newBill = Billionaire(bill_id = id, name = name,
                                      age = age, worth = worth,
                                      category = category,
                                      citizenship = citizenship,
                                      gender = gender, connectedTo = [])
                newBill.save()
                answer = f'Successfully added {newBill.name}'
            return render_template('results1_1.html', answer = answer)
        return render_template('base1_1.html')

    @app.route('/del_user', methods = ['POST', 'GET'])
    def del_user():
        '''Delete an existing user by entering their
           name in the form.'''


        if request.method == 'POST':
            f0 = request.form.get('search1_7')
            try:
                b = Billionaire.objects(name = f0)[0]
                connections = Billionaire.objects(connectedTo__contains = b)
                for connection in connections:
                    connection.del_connection(b)
                    connection.save()
                answer = f'{b.name} has been deleted'
                b.delete()
            except IndexError:
                answer = f'{f0} does not exist in the database'
            return render_template('results1_2.html', answer = answer)
        return render_template('base1_2.html')

    @app.route('/add_friend', methods = ['POST', 'GET'])
    def add_friend():
        '''Choose a document in the database by name, then choose
           another document to add a connection to.'''


        if request.method == 'POST':
            f1 = request.form.get('search2')
            f2 = request.form.get('search3')
            try:
                f1o = Billionaire.objects(name = f1)[0]
                f2o = Billionaire.objects(name = f2)[0]
            except IndexError:
                return redirect(url_for('add_friend'))        
            added = f1o.add_connection(f2o)
            if added:
                f1o.save()
                answer = f'{f1o.name} is now friends with {f2o.name}'
            else:
                answer = f'{f1o.name} is already friends with {f2o.name}'
            return render_template('results2.html', answer = answer)        
        return render_template('base2.html')
        
    @app.route('/del_friend', methods = ['POST', 'GET'])
    def del_friend():
        '''Delete a connection from the adjacency list
           of a specified document. The route refreshes
           itself when a non existing document is queried.'''


        if request.method == 'POST':

            f1 = request.form.get('search4')
            f2 = request.form.get('search5')
            try:    
                f10 = Billionaire.objects(name = f1)[0]
                f20 = Billionaire.objects(name = f2)[0]
            except IndexError:
                return redirect(url_for('del_friend'))
            if f20 in f10.get_connections():
                f10.del_connection(f20)
                f10.save()
                answer = f'''{f10.name} is no longer friends
                          with {f20.name}'''
            else:
                answer = f'{f10.name} is not friends with {f20.name}'
            return render_template('results3.html', answer = answer)
        return render_template('base3.html')
    
    @app.route('/network_search', methods = ['POST', 'GET'])
    def network_search():
        '''This route requests the name of an existing user, and
           returns a dictionary containing all levels of connections.
           '''

           
        graph = Graph()
        if request.method == 'POST':
            f0 = request.form.get('search6')
            try:
                f1 = Billionaire.objects(name = f0)[0]
            except IndexError:
                return redirect(url_for('network_search'))
            for bill in Billionaire.objects():
                graph.addBillionaire(bill)
            visited, layers = breadthFirstSearch(graph, f1)
            return layers
        return render_template('base4.html')

    @app.route('/display_friends', methods = ['POST', 'GET'])
    def display_friends():
        '''Enter the name of an existing user and view all
           of the first level connections of that user'''


        if request.method == 'POST':
            f0 = request.form.get('search7')
            try:
                querybill = Billionaire.objects(name = f0)[0]
                answer = str([b.name for b in querybill.get_connections()])
                return render_template('results4.html', answer = answer)
            except IndexError:
                return redirect(url_for('display_friends'))
        return render_template('base5.html')

    @app.route('/load_database')
    def load_database():
        """Load the forbes csv file into a mongoengine collection.
           Function only need to be run one time, before using
           the root, drop or another querying function. The function
           also returns the number of duplicate names captured. The
           net values in the csv have a unit size of $1 mil and need
           to be converted by multiplication with 1 million."""


        if not Billionaire.objects().count():
            c = 0
            df = pd.read_csv('forbes_2022_billionaires.csv')
            feats = '''personName age finalWorth category
                       countryOfCitizenship gender'''.split()
            df = df[feats]
            df.dropna(inplace = True)
            df['finalWorth'] = df['finalWorth'].astype(int) * 1000000
            ldf = len(df)

            for x in range(ldf//10):
                entry = df.iloc[x].values
                if not Billionaire.objects(
                    name__icontains = entry[0]
                    ).count():
                    b = Billionaire(
                        bill_id = x, name = entry[0], age = entry[1],
                        worth = entry[2], category = entry[3],
                        citizenship = entry[4], gender = entry[5],
                        connectedTo = [])
                    b.save()
                else:
                    c += 1
            return(f'''Database successfully loaded {ldf//10 - c}
                   docs and removed {c} duplicates''')
        return 'Database is up to date'

    @app.route('/drop_database')
    def drop_database():
        Billionaire.drop_collection()
        return 'Database has been wiped'

    @app.route('/view_database')
    def view_database():
        '''View all of the names associated with objects in
           the database.'''


        return str([b.name for b in Billionaire.objects()])

    @app.route('/bfs')
    def bfs():
        '''This testing route loads a graph with billionaires from
        the database, giving the billioinaire named Larry Page
        connections to 2 other billionaires(in the graph as well as
        the database), then those connections are given connections,
        and so forth for four iterations. Each object below must be
        in the database in order to run this route. Finally, view
        results of a breadth first search, showing Mr. Page's first
        level connections, second and so on.'''


        querybill = Billionaire.objects(name = 'Larry Page')[0]
        qb2 = Billionaire.objects(name = 'Mark Zuckerberg')[0]
        qb25 = Billionaire.objects(name = 'Bill Gates')[0]
        qb3 = Billionaire.objects(name = 'Miriam Adelson')[0]
        qb35 = Billionaire.objects(name = 'Robin Zeng')[0]
        qb4 = Billionaire.objects(name = 'Guillaume Pousaz')[0]
        qb45 = Billionaire.objects(name = 'Klaus-Michael Kuehne')[0]
        qb46 = Billionaire.objects(name = 'Julia Koch & family')[0]
        qb5 = Billionaire.objects(name = 'Lee Shau Kee')[0]
        qb55 = Billionaire.objects(name = 'Mukesh Ambani')[0]
        qb56 = Billionaire.objects(name = 'Warren Buffett')[0]
        qb57 = Billionaire.objects(name = 'Michael Bloomberg')[0]
        graph = Graph()
        bills = Billionaire.objects()
        for bill in bills:
            graph.addBillionaire(bill)
        graph.addEdge(querybill, qb2)
        graph.addEdge(querybill, qb25)
        graph.addEdge(qb2, qb3)
        graph.addEdge(qb2, qb35)
        graph.addEdge(qb3, qb4)
        graph.addEdge(qb3, qb45)
        graph.addEdge(qb3, qb46)
        graph.addEdge(qb4, qb5)
        graph.addEdge(qb4, qb55)
        graph.addEdge(qb4, qb56)
        graph.addEdge(qb4, qb57)
        querybill.add_connection(qb2)
        querybill.add_connection(qb25)
        querybill.save()
        qb2.add_connection(qb3)
        qb2.add_connection(qb35)
        qb2.save()
        qb3.add_connection(qb4)
        qb3.add_connection(qb45)
        qb3.add_connection(qb46)
        qb3.save()
        qb4.add_connection(qb5)
        qb4.add_connection(qb55)
        qb4.add_connection(qb56)
        qb4.add_connection(qb57)
        qb4.save()
        visited, layers = breadthFirstSearch(graph, querybill)
        return layers

    db.disconnect(alias = DB_URI)
    return app
