#!/usr/bin/python
'''
Author: Ricky Tham
Project: Item Catalog Web Application
'''
from flask import Flask, render_template, request, redirect
from flask import jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc, exc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CatItem, User
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# Store CLIENT_ID stuff here
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

engine = create_engine('sqlite:///categorycatalogwithusers.db',
                       connect_args={"check_same_thread": False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# -------------- STORE LOGIN STUFF HERE -------------

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have Successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in.")
        return redirect(url_for('showCategories'))


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnted.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for a given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.SQLAlchemyError:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# -------------- END LOGIN STUFF HERE ---------------

# -------------- STORE JSON STUFF HERE --------------

# Show JSON of all categories and all items


@app.route('/catalog.json')
def categoriesWithItemsJSON():
    catList = []
    categories = getCategories()
    for category in categories:
        serializeCat = category.serialize
        items = session.query(CatItem).filter_by(cat_id=category.id).all()
        serializeCat['Item'] = [i.serialize for i in items]
        catList.append(serializeCat)
    return jsonify(Category=catList)

# Show JSON of all categories only


@app.route('/catalog/categories/JSON/')
def categoriesJSON():
    categories = getCategories()
    return jsonify(Category=[category.serialize for category in categories])


@app.route('/catalog/<cat_name>/JSON/')
@app.route('/catalog/<cat_name>/items/JSON')
def catItemsJSON(cat_name):
    category = session.query(Category).filter_by(name=cat_name).one()
    serializeCat = category.serialize
    items = session.query(CatItem).filter_by(cat_id=category.id).all()
    serializeCat['Item'] = [i.serialize for i in items]
    return jsonify(Category=serializeCat)

# Show JSON of a CatItem


@app.route('/catalog/<cat_name>/<catItem_name>/JSON/')
def itemJSON(cat_name, catItem_name):
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(CatItem).filter_by(
        cat_id=category.id, name=catItem_name).one()
    return jsonify(CatItem=item.serialize)


# --------------  END JSON STUFF HERE  --------------


# ------------- STORE CATALOG CODE HERE -------------


# Show all categories
@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = getCategories()
    catItems = session.query(CatItem, Category).filter(
        Category.id == CatItem.cat_id).order_by(
        desc(CatItem.id)).limit(9).from_self()
    if 'username' not in login_session:
        return render_template('public_categories.html',
                               categories=categories, catItems=catItems)
    else:
        return render_template('categories.html', categories=categories,
                               catItems=catItems)

# Show all CatItems for the specific category


@app.route('/catalog/<cat_name>/')
@app.route('/catalog/<cat_name>/items/')
def showCatItems(cat_name):
    categories = getCategories()
    category = session.query(Category).filter_by(name=cat_name).one()
    items = session.query(CatItem).filter_by(cat_id=category.id).all()
    itemLen = len(items)
    if 'username' not in login_session:
        return render_template('public_category.html', itemLen=itemLen,
                               category=category, items=items,
                               categories=categories)
    else:
        return render_template('category.html', itemLen=itemLen,
                               category=category, items=items,
                               categories=categories)

# Show the specific CatItem for the specific category


@app.route('/catalog/<cat_name>/<catItem_name>/')
def showItem(cat_name, catItem_name):
    category = session.query(Category).filter_by(name=cat_name).one()
    item = session.query(CatItem).filter_by(
        cat_id=category.id, name=catItem_name).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('public_cat_item.html', item=item,
                               cat_name=cat_name)
    else:
        return render_template('catitem.html', item=item, cat_name=cat_name)

# Create a new category item


@app.route('/catalog/item/new/', methods=['GET', 'POST'])
def newCatItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newItem = CatItem(name=request.form['name'],
                          description=request.form['description'],
                          cat_id=category.id,
                          user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New %s Item Successfully Created for %s' %
              (newItem.name, category.name))
        return redirect(url_for('showCategories'))
    else:
        categories = getCategories()
        return render_template('newcatitem.html', categories=categories)

# Edit a category item


@app.route('/catalog/<cat_name>/<catItem_name>/edit/', methods=['GET', 'POST'])
def editCatItem(cat_name, catItem_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=cat_name).one()
    editedItem = session.query(CatItem).filter_by(
        name=catItem_name, cat_id=category.id).one()
    if editedItem.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " + \
            "authorized to edit this item. Please create your own item " + \
            "in order to edit.'); window.location.href = \"/catalog\";}" + \
            "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category']:
            editedCategory = session.query(Category).filter_by(
                name=request.form['category']).one()
            editedItem.cat_id = editedCategory.id
        session.add(editedItem)
        session.commit()
        flash('Category Item Successfully Edited')
        return redirect(url_for('showItem', cat_name=request.form['category'],
                                catItem_name=request.form['name']))
    else:
        categories = getCategories()
        return render_template('editcatitem.html', currCategory=category,
                               categories=categories, item=editedItem)


# Delete a category item
@app.route('/catalog/<cat_name>/<catItem_name>/delete/',
           methods=['GET', 'POST'])
def deleteCatItem(cat_name, catItem_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=cat_name).one()
    itemToDelete = session.query(CatItem).filter_by(
        name=catItem_name, cat_id=category.id).one()
    if itemToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " + \
            "authorized to edit this item. Please create your own item " + \
            "in order to edit.'); window.location.href = \"/catalog\";}" + \
            "</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Catalog Item Successfully Deleted')
        return redirect(url_for('showCatItems', cat_name=cat_name))
    else:
        return render_template('deletecatitem.html', cat_name=cat_name,
                               item=itemToDelete)

# Grabs the categories and sorts them by name in ascending order


def getCategories():
    return session.query(Category).order_by(asc(Category.name))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
