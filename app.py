from flask import Flask, render_template, request
import pandas as pd
import requests as req
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:lolek123@localhost/datascience'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

class Countries(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    country_name = db.Column(db.String,nullable=False)
    country_code = db.Column(db.String,nullable=False)

    def __init__(self,country_name,country_code):
        self.country_name = country_name
        self.country_code = country_code

    def __str__(self):
        return f"ID : {self.id} Country name : {self.country_name} Country code : {self.country_code}"

#db.create_all() create Database



def getdata(country_code):
    link = req.get(f'https://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.CD?format=json')
    linkjson = list(link.json())
    pdata = pd.DataFrame(linkjson[1])
    pdata = pdata.dropna(axis=0)
    return pdata


def countries():
    strony = req.get('https://api.worldbank.org/v2/country/all?format=json&per_page=399')
    countries = pd.DataFrame(strony.json()[1])
    return countries


# worldbankcountries = countries()
# for k in worldbankcountries['id']:
#     db.session.add(Countries(worldbankcountries['name'][list(worldbankcountries['id']).index(k)],k))
#
# db.session.commit() // Insert countries from worlbank to database

def getAll():
    return Countries.query.all()

def getOne(id):
    return Countries.query.get(id)

@app.route('/')
def hello_world():
    return render_template('home.html', countries=countries()[0], countrieslength=countries()[1])


@app.route('/', methods=['GET', 'POST'])
def showgraph():
    panstwo = request.form.get('selected_country')
    data = getdata(panstwo)
    vvalues = data['value'].tolist()
    llabel = data['date'].tolist()
    vvalues.reverse()
    llabel.reverse()
    return render_template('home.html', country=panstwo, labels=llabel, values=vvalues, countries=countries()[0],
                           countrieslength=countries()[1])


if __name__ == '__main__':
    app.run()
