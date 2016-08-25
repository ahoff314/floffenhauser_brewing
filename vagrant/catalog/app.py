from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Brewery, Beer

engine = create_engine('sqlite:///brew.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# MAKING an API endpoint GET

@app.route('/breweries/<int:brewery_id>/beers/JSON')
def beersJSON(brewery_id):
    brewery = session.query(Brewery).first()
    beers = session.query(Beer).filter_by(brewery_id=brewery.id)
    return jsonify(Beer=[i.serialize for i in beers])

# HOME PAGE
@app.route('/')
def home():
    brewery = session.query(Brewery).all()
    return render_template('index.html', brewery=brewery)

# BREWERY INFO PAGE
@app.route('/breweries/<int:brewery_id>/')
def index(brewery_id):
    brewery = session.query(Brewery).first()
    beers = session.query(Beer).filter_by(brewery_id=brewery.id)
    return render_template('beers.html', brewery=brewery, beers=beers)

# NEW BEER ROUTE
@app.route('/breweries/<int:brewery_id>/new/', methods=['GET', 'POST'])
def newBeer(brewery_id):
    if request.method == 'POST':
        newBeer = Beer(name=request.form['name'], brewery_id=brewery_id)
        session.add(newBeer)
        session.commit()
        flash('New beer has been added. Cheers!')
        return redirect(url_for('index', brewery_id=brewery_id))
    else:
        return render_template('newbeer.html', brewery_id=brewery_id)

# EDIT BEER ROUTE
@app.route('/breweries/<int:brewery_id>/<int:id>/edit/', methods=['GET', 'POST'])
def editBeer(brewery_id, id):
    editedItem = session.query(Beer).filter_by(id=id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("This beer has been successfully edited. Cheers!")
        return redirect(url_for('index', brewery_id=brewery_id))
    else:
        return render_template('editbeer.html', brewery_id=brewery_id, i=editedItem)

# DELETE BEER ROUTE
@app.route('/breweries/<int:brewery_id>/<int:id>/delete/', methods=['GET', 'POST'])
def deleteBeer(brewery_id, id):
    itemToDelete = session.query(Beer).filter_by(id=id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash("This beer has been removed.")
        return redirect(url_for('index', brewery_id = brewery_id))
    else:
        return render_template('deletebeer.html', i = itemToDelete)

# ABOUT ROUTE
@app.route('/about')
def about():
    return render_template('about.html')

# 404

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



if __name__ == '__main__':
    app.secret_key = 'super_secret'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
