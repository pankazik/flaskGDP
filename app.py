from flask import Flask, render_template, request
import pandas as pd
import requests as req
from flask_sqlalchemy import SQLAlchemy
from sklearn.linear_model import LinearRegression
from pandas.core.groupby.groupby import DataError


# import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://demo:demo@localhost/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_DEBUG'] = 1
db = SQLAlchemy(app)


class Countries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)

    def __init__(self, country_name, country_code):
        self.country_name = country_name
        self.country_code = country_code

    def __str__(self):
        return f"{self.country_name}"

    def todict(self):
        return {'id': self.id, 'country_name': self.country_name, 'country_code': self.country_code}


# db.create_all()
# create database "Countries"


def getdata(country_code):
    link = req.get(f'https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json')
    linkjson = list(link.json())
    pdata = pd.DataFrame(linkjson[1])
    pdata = pdata.dropna(axis=0)
    return pdata


def countries():
    strony = req.get('https://api.worldbank.org/v2/country/all?format=json&per_page=399')
    pdcountries = pd.DataFrame(strony.json()[1])
    return pdcountries


# worldbankcountries = countries()
# for k in worldbankcountries['id']:
#     db.session.add(Countries(worldbankcountries['name'][list(worldbankcountries['id']).index(k)],k))
#
# db.session.commit()
# insert data from worldbank to database countries

def getall():
    return Countries.query.all()


def getane(country_id):
    return Countries.query.get(country_id)


@app.route('/')
def hello_world(*error):
    dbcountries = getall()
    return render_template('home.html', countries=dbcountries, countrieslength=int(len(dbcountries)),error=error)


@app.route('/', methods=['GET', 'POST'])
def showgraph():
    panstwo = request.form.get('selected_country')
    countryname = Countries.query.filter(Countries.country_code == panstwo).first()
    data = getdata(panstwo)
    try:
        vvalues = data['value'].tolist()
        llabel = data['date'].tolist()
        vvalues.reverse()
        llabel.reverse()
        y = pd.array(data['value'], dtype='f')
        x = pd.array(data['date'], dtype='f').reshape((-1, 1))
        linear = LinearRegression().fit(x, y)
        lineardata = data['date'].copy().astype('float') * linear.coef_ + linear.intercept_
        lineardata = lineardata.tolist()
        lineardata.reverse()
        dbcountries = getall()
        return render_template('home.html', country=countryname, labels=llabel, values=vvalues, countries=dbcountries,
                               countrieslength=int(len(dbcountries)), lineardata=lineardata, r2=linear.score(x, y))
    except KeyError as error:
        print(error)
    except DataError as error:
        print(error)
    return hello_world()


if __name__ == '__main__':
    app.run()
