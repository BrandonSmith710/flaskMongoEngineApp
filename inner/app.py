import mongoengine as me
from flask import Flask, render_template, request, Response
from flask_mongoengine import MongoEngine
from .modelgorithm import Billionaire, Graph, breadthFirstSearch
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
        """This route asks for a range of two values, separated
        by a space; returned is a set of billionaire 
        objects with a net worth value falling in the specified
        range(values are no longer current)."""


        if request.method == 'POST':
            w = request.form.get('search').split()
            if all(arg.isdigit() for arg in w):
                if len(w) == 2:
                    worth_l, worth_u = int(w[0]), int(w[1])
                    bills = Billionaire.objects(
                        worth__gte = worth_l,
                        worth__lte = worth_u,
                        )
                    worths = set(bill.worth for bill in bills)
                    groups = {f'${worth}': [
                    bill.name for bill in bills if bill.worth == worth
                    ] for worth in worths
                    }
                else:
                    return render_template('base.html')
                return render_template('results.html', answer = groups)
            else:
                return render_template('base.html')
        return render_template('base.html')

    @app.route('/query_by_citizenship', methods = ['GET', 'POST'])
    def query_by_citizenship():
        """This route accepts a country name and returns
           all billionaire objects with a citizenship
           value equal to the input country"""


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
            except:
                return render_template('base1.html')
        return render_template('base1.html')

    @app.route('/load_database')
    def load_database():
        """Load the forbes csv file into a mongoengine collection.
           Function only need to be run one time, before using
           the root, drop or another querying function. The function
           also returns the number of duplicate names captured. The
           net values in the csv have a unit size of $1 mil and need
           to be converted by multiplication with 1 million"""


        if not Billionaire.objects().count():
            c = 0
            # billionaire_list = []
            df = pd.read_csv('forbes_2022_billionaires.csv')
            feats = '''personName age finalWorth category
                       countryOfCitizenship gender'''.split()
            df = df[feats]
            df.dropna(inplace = True)
            df['finalWorth'] = df['finalWorth'].astype(int) * 1000000
            ldf = len(df)

            for x in range(ldf//25):
                entry = df.iloc[x].values
                # if not x in billionaire_list:
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
            return(f'''Database successfully loaded {ldf//25 - c}
                   docs and removed {c} duplicates''')
        return 'Database is up to date'

    @app.route('/drop_database')
    def drop_database():
        Billionaire.drop_collection()
        return 'Database has been wiped'

    @app.route('/view_graph')
    def view_graph():
        qb2 = Billionaire.objects(name = 'Mark Zuckerberg')[0]
        qb3 = Billionaire.objects(name = 'Miriam Adelson')[0]
        return str([b.name for b in Billionaire.objects(name = 'Larry Page')[
            0].connectedTo]) + str([b.name for b in qb2.connectedTo]) + str(
            [b.name for b in qb3.connectedTo])

    @app.route('/alter_friends')
    def alter_friends():
        
        querybill = Billionaire.objects(name = 'Larry Page')[0]
        print((querybill.name, querybill.bill_id))
        qb2 = Billionaire.objects(name = 'Mark Zuckerberg')[0]
        qb3 = Billionaire.objects(name = 'Miriam Adelson')[0]
        qb4 = Billionaire.objects(name = 'Guillaume Pousaz')[0]

        querybill.add_connection(qb2)
        qb2.add_connection(qb3)
        qb3.add_connection(qb4)
            
        querybill.save()
        qb2.save()
        qb3.save()

        return str([b.name for b in querybill.connectedTo]) + str(
            [b.name for b in qb2.connectedTo]) + str([b.name for b in qb3.connectedTo])

    @app.route('/add_friend')
    def add_friend():
        return 'hello'
        
    @app.route('/bfs')
    def bfs():
        graph = Graph()
        bill_list = Billionaire.objects()
        for bill in bill_list:
            graph.addBillionaire(bill)
        larry_p = Billionaire.objects(name = 'Larry Page')[0]
        visited, layers = breadthFirstSearch(graph, larry_p)
        return str(layers)

    print('Billionaires:', Billionaire.objects.count())

    db.disconnect(alias=DB_URI)
    return app
