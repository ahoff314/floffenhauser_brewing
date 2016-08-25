from flask import Flask, redirect, render_template, request, url_for
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

# Create route for new beer CLEAN UP ROUTE NAMES  intuitive

@app.route('/breweries/<int:brewery_id>/new/', methods=['GET', 'POST'])
def newBeer(brewery_id):
    if request.method == 'POST':
        newBeer = Beer(name=request.form['name'], brewery_id=brewery_id)
        session.add(newBeer)
        session.commit()
        return redirect(url_for('index', brewery_id=brewery_id))
    else:
        return render_template('newbeer.html', brewery_id=brewery_id)

# Create route for edit beers
@app.route('/breweries/<int:brewery_id>/<int:id>/edit/', methods=['GET', 'POST'])
def editBeer(brewery_id, id):
    editedItem = session.query(Beer).filter_by(id=id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('index', brewery_id=brewery_id))
    else:
        return render_template('newbeer.html', brewery_id=brewery_id, i=editedItem)

#create route for delete beers

@app.route('/breweries/<int:brewery_id>/<int:id>/delete/', methods=['GET', 'POST', 'DELETE'])
def deleteBeer(brewery_id, id):
    if request.method == 'POST':
        newBeer = Beer(name=request.form['name'], brewery_id=brewery_id)
        session.add(newBeer)
        session.commit()
        return redirect(url_for('index', brewery_id=brewery_id))
    else:
        return render_template('newbeer.html', brewery_id=brewery_id)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
