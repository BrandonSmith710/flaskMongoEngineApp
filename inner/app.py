import mongoengine as me
from flask import Flask, render_template, request, Response
from flask_mongoengine import MongoEngine
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

    class Billionaire(me.Document):
        name = me.StringField(required = True, unique = True)
        age = me.IntField(required = True)
        worth = me.IntField(required = True)
        category = me.StringField(required = True)
        citizenship = me.StringField(required = True)
        gender = me.StringField(required = True)

        def to_json(self):
            return {
                'name': self.name,
                'age': self.age,
                'worth': self.worth,
                'category': self.category,
                'citizenship': self.citizenship,
                'gender': self.gender
            }

    @app.route('/', methods=['GET', 'POST'])
    def root():
        """This route asks for a range of two values, separated
        by a space; What is returned is an assortment of
        billionaires whose net worth falls in the specified
        range(the net worth values are no longer current)."""


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

    @app.route('/query_by_citizenship', methods=['GET', 'POST'])
    def query_by_citizenship():
        """This querying route accepts a country name and returns
           all billionaire object-documents with a citizenship
           value equal to the input country"""


        if request.method == 'POST':
            w = request.form.get('search1')
            try:
                bills = Billionaire.objects(citizenship__iwholeword=w)
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
        """This route will load the csv file into a mongoengine
           collection, and therefore should only need to be run
           one time, before using the root or other querying
           route. The function also sifts out and returns the number
           of duplicate names that were prevented from being entered.
           The net worth values in the csv have a unit size of $1 mil
           and need to be converted by multiplying by 1 million"""


        if not Billionaire.objects().count():
            c = 0
            df = pd.read_csv('forbes_2022_billionaires.csv')
            feats = '''personName age finalWorth category
                       countryOfCitizenship gender'''.split()
            df = df[feats]
            df.dropna(inplace=True)
            ldf = len(df)
            for x in range(ldf):
                row = df.iloc[x].values
                entry = []
                for ind, item in enumerate(row):
                    if type(item) == str:
                        entry += [item]
                    else:
                        i = int(item)
                        if ind == 2:
                            i *= 1000000
                        entry += [i]
                if not Billionaire.objects(
                    name__icontains = entry[0]
                    ).count():
                    b = Billionaire(
                        name = entry[0], age = entry[1],
                        worth = entry[2], category = entry[3],
                        citizenship = entry[4], gender = entry[5]
                        )
                    b.save()
                else:
                    c += 1
            return f'''Database successfully loaded {ldf - c}
                       documents, removed {c} duplicates'''
        return 'Database is up to date'

    @app.route('/drop_database')
    def drop_database():
        Billionaire.drop_collection()
        return 'Database has been wiped'

    print('Billionaires:', Billionaire.objects.count())

    db.disconnect(alias=DB_URI)

    return app