from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Brewery, Beer

from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///brew.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# LOGIN ROUTE
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')

@app.route('/gconnect', methods = ['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state passed'), 401)
        response.headers['Content-type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# API endpoint GET for all beers, specific beers, and all breweries
@app.route('/breweries/<int:brewery_id>/beers/JSON')
def beersJSON(brewery_id):
    brewery = session.query(Brewery).first()
    beers = session.query(Beer).filter_by(brewery_id=brewery.id)
    return jsonify(Beer=[i.serialize for i in beers])

@app.route('/breweries/<int:brewery_id>/beers/<int:id>/JSON')
def specificBeerJSON(brewery_id, id):
    brewery = session.query(Brewery).first()
    beers = session.query(Beer).filter_by(id=id)
    return jsonify(Beer=[i.serialize for i in beers])

@app.route('/breweries/JSON')
def breweriesJSON():
    brewery = session.query(Brewery).all()
    beers = session.query(Brewery).filter_by(id=id)
    return jsonify(Brewery=[i.serialize for i in brewery])


# HOME PAGE
@app.route('/')
def home():
    brewery = session.query(Brewery).all()
    return render_template('index.html', brewery=brewery)


# PARTICIPATING BREWERIES WITH LINKS
@app.route('/breweries/')
def showBreweries():
    breweries = session.query(Brewery).all()
    return render_template('breweries.html', breweries=breweries)

# EACH BREWERY INFO PAGE
@app.route('/breweries/<int:brewery_id>/')
def index(brewery_id):
    brewery = session.query(Brewery).filter_by(id=brewery_id).one()
    beers = session.query(Beer).filter_by(brewery_id=brewery.id)
    return render_template('beers.html', brewery=brewery, beers=beers)


# NEW BREWERY ROUTE
@app.route('/brewery/new/', methods=['GET', 'POST'])
def newBrewery():
    if request.method == 'POST':
        newBrewery = Brewery(name=request.form['name'])
        session.add(newBrewery)
        session.commit()
        flash('Your brewery has been added. Cheers!')
        return redirect(url_for('home'))
    else:
        return render_template('newbrewery.html')


# EDIT BREWERY
@app.route('/breweries/<int:brewery_id>/edit/', methods=['GET', 'POST'])
def editBrewery(brewery_id):
    editedBrewery = session.query(Brewery).filter_by(id=brewery_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedBrewery.name = request.form['name']
            session.add(editedBrewery)
            session.commit()
            flash("This brewery has been successfully edited. Cheers!")
        return redirect(url_for('home'))
    else:
        return render_template('editbrewery.html', brewery=editedBrewery)


# DELETE BREWERY
@app.route('/breweries/<int:brewery_id>/delete/', methods=['GET', 'POST'])
def deleteBrewery(brewery_id):
    breweryToDelete = session.query(Brewery).filter_by(id=brewery_id).one()
    if request.method == 'POST':
        session.delete(breweryToDelete)
        session.commit()
        flash("This brewery has been removed.")
        return redirect(url_for('home'))
    else:
        return render_template('deletebrewery.html', brewery = breweryToDelete)



# NEW BEER ROUTE
@app.route('/breweries/<int:brewery_id>/new/', methods=['GET', 'POST'])
def newBeer(brewery_id):
    if request.method == 'POST':
        newBeer = Beer(name=request.form['name'], style=request.form['style'], brewery_id=brewery_id)
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
    app.run(host='0.0.0.0', port=5000)
