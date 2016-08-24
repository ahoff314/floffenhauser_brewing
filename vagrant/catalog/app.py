from flask import Flask, redirect, render_template
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup  import Base, Brewery, Beer

engine = create_engine('sqlite:///brew.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/breweries/<int:brewery_id>/')
def index(brewery_id):
    brewery = session.query(Brewery).first() # SHould we use dot first??
    beers = session.query(Beer).filter_by(brewery_id=brewery.id)
    return render_template('beers.html', brewery=brewery, beers=beers)

# Create route for new beer CLEAN UP ROUTE NAMES more intuitive

@app.route('/breweries/<int:brewery_id>/new/')
def newBeer(brewery_id):
    return " put a form here and verify permissions to add a new beer"

# Create route for edit beeers
@app.route('/breweries/<int:brewery_id>/<int:id>/edit/')
def editBeer(brewery_id, id):
    return " put a form here and verift authorization to edit beers"

#create route for delete beers

@app.route('/breweries/<int:brewery_id>/<int:id>/delete/')
def deleteBeer(brewery_id, id):
    return " put a form here and verify authorization to delete brews"


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
