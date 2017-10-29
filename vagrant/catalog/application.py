from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from setup_db import Base, Sport, CategoryItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from datetime import datetime
import re
from pprint import pprint

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Sports Items Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemscatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def querySports():
    # In this function, I am retrieving and displaying all the sports
    # from the database.
    sb = session.query(Sport).order_by(asc(Sport.name))
    return sb


def current_date():
    # In this function, I need to put dates on each item so that
    # in my main page, it will display the recently added items
    # according to the date they were created on.
    new_date = re.sub(r'-', "", str(datetime.now()))
    new_date = re.sub(r':', "", new_date)
    new_date = re.sub(r' ', "", new_date)
    new_date = float(new_date)
    return new_date


@app.route('/')
@app.route('/sports/')
def showSports():
    # Show all sports
    print 'called ShowSports()'
    lt = session.query(CategoryItem).order_by(desc(CategoryItem.date))
    sb = querySports()
    print 'sports query: ' + str(sb)
    return render_template(
        'index.html', show_sports=sb, latest_items=lt, page='latest_items')

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    # Displaying my Google Login Button.
    sb = querySports()
    print 'called showLogin()'
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print 'login_session["state"]' + str(login_session['state'])
    print "calling login.html"
    return render_template(
        'index.html', STATE=state, page='login', show_sports=sb)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # In this function, I am attempting to log into the Google Account.
    print 'called gconnect()'
    # Validate state token
    print 'request.args.get("state"): '+request.args.get('state')
    print 'login_session["state"]: '+login_session['state']
    if request.args.get('state') != login_session['state']:
        print "request.args.get('state') != login_session['state']"
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'response: ' + str(response)
        return response
    else:
        print "request.args.get('state') == login_session['state']... MATCH!"
    code = request.data
    print 'code: '+code

    try:
        # Upgrade the authorization code into a credentials object
        print 'begin trying to upgrade the authorization code into a ' \
            'credentials object'
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print 'oauth_flow: ' + str(oauth_flow)
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print 'credentials: '+str(credentials)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'response: '+str(response)
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    print 'access_token: '+access_token
    print 'url: '+url
    print 'h: '+str(h)
    print 'result: '+str(result)
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print "there was an error in the access token info, abort"
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        print 'response: '+str(response)
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print 'gplus_id: ' + str(gplus_id)
    if result['user_id'] != gplus_id:
        print "result['user_id'] != gplus_id"
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print 'response: '+str(response)
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print "result['issued_to'] != CLIENT_ID"
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        print 'response: '+str(response)
        return response

    stored_access_token = login_session.get('access_token')
    print 'stored_access_token: '+str(stored_access_token)
    stored_gplus_id = login_session.get('gplus_id')
    print 'stored_gplus_id: '+str(stored_gplus_id)
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        print "stored_access_token is not None and gplus_id == stored_gplus_id"
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        print 'response: '+str(response)
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    print "login_session['access_token']: "+login_session['access_token']
    print "login_session['gplus_id']: "+login_session['gplus_id']

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    print "userinfo_url: " + userinfo_url
    print "params: " + str(params)
    print "answer: " + str(answer)

    data = answer.json()
    print 'data: ' + str(data)

    login_session['username'] = data['name']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    print "login_session['username']: "+login_session['username']
    print "login_session['email']: "+login_session['email']

    # check if email exists in the database...
    print 'data["email"] is: ' + str(data["email"])
    user_id = getUserID(data["email"])
    print 'user_id: ' + str(user_id)
    if not user_id:
        print 'user_id not'
        flash("Sorry you are not authorized.")
    else:
        print 'user_id is'
        login_session['user_id'] = user_id
        print "login_session['user_id'] " + str(login_session['user_id'])
        flash("Welcome back, you are now logged in as %s" %
              login_session['username'])
        print "done!"
    return redirect(url_for('showSports'))


def getUserID(email):
    # In this function, I am matching the email in the database to the
    # email the user attempted to log in with.
    print 'called getUserID(email)'
    try:
        user = session.query(User).filter_by(email=email).one()
        print 'user: '+str(user)
        return user.id
    except:
        print 'None'
        return None


@app.route('/gdisconnect')
def gdisconnect():
    # DISCONNECT - Revoke a current user's token and reset their login_session
    print 'called gdisconnect()'
    # Only disconnect a connected user.
    print 'login_session[]: ' + str(login_session)
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', str(access_token)
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'access_token: ' + access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
        login_session['access_token']
    print 'url: ' + url
    h = httplib2.Http()
    print 'h: ' + str(h)
    result = h.request(url, 'GET')[0]
    print 'result: ' + str(result)
    if result['status'] == '200':
        print "result['status'] == '200'"
        print login_session['access_token']
        print login_session['gplus_id']
        print login_session['username']
        print login_session['email']
    else:
        print "result['status'] != '200' ... Failed to revoke token."
        print "result['status'] is: " + str(result['status'])
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['user_id']
    flash('Successfully Logged Out')
    return redirect(url_for('showSports'))


# JSON API to view all inventory in a certain sport
@app.route('/sport/<int:sport_id>/items/JSON')
def SportAndItemsJSON(sport_id):
    print 'called SportAndItemsJSON(restaurant_id)'
    sport = session.query(Sport).filter_by(id=sport_id).one()
    cat_items = session.query(CategoryItem).filter_by(
        sport_id=sport_id).all()
    print 'sport: ' + str(sport)
    print 'cat_item: ' + str(cat_items)
    return jsonify(category_item=[i.serialize for i in cat_items])


# JSON API to view a certain item in a certain sport inventory
@app.route('/sport/<int:sport_id>/items/<int:item_id>/JSON')
def SportsItemsListJSON(sport_id, item_id):
    print 'called SportsItemsListJSON(sport_id, item_id)'
    Sport_Item = session.query(CategoryItem).filter_by(id=item_id).one()
    print 'Sport_Item: '+str(Sport_Item)
    return jsonify(Sport_Item=Sport_Item.serialize)


# JSON API to view all sports
@app.route('/sport/JSON')
def SportsJSON():
    print 'called SportsJSON()'
    sports = session.query(Sport).all()
    print 'sports: '+str(sports)
    return jsonify(sports=[r.serialize for r in sports])


@app.route('/sport/new/', methods=['GET', 'POST'])
def newSport():
    # Function to add a new sport category.
    sb = querySports()
    print 'called newSport()'
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    if request.method == 'POST':
        print "request.method == 'POST'"
        newSport = Sport(
            name=request.form['name'], user_id=login_session['user_id'])
        print 'newSport Query: ' + str(newSport)
        print 'name of new sport is ' + str(request.form['name'])
        print 'user_id is ' + str(login_session['user_id'])
        session.add(newSport)
        flash('New Sport Category %s Successfully Created' % newSport.name)
        session.commit()
        return redirect(url_for('showSports'))
    else:
        print "request.method != 'POST'"
        print 'calling newSport.html'
        return render_template(
            'index.html', page='newSport', show_sports=sb)


# Edit a Sport
@app.route('/sport/<int:sport_id>/edit/', methods=['GET', 'POST'])
def editSport(sport_id):
    # Function to edit an existing sport category.
    sb = querySports()
    print 'called editSport(sport_id)'
    editedSport = session.query(
        Sport).filter_by(id=sport_id).one()
    print 'sport_id: ' + str(sport_id)
    print 'editedSport: ' + str(editedSport)
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    if editedSport.user_id != login_session['user_id']:
        print "editedSport.user_id != login_session['user_id']"
        return "<script>function myFunction() {alert('You are not authorized' \
            'to edit this restaurant. Please create your own restaurant' \
            'in order to edit.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print "request.method == 'POST'"
        if request.form['name']:
            print "request.form['name'] has something"
            editedSport.name = request.form['name']
            print "editedSport.name: "+str(editedSport.name)
            flash('Sport Successfully Edited %s' % editedSport.name)
            return redirect(url_for('showSports'))
    else:
        print "request.method != 'POST'"
        print "calling 'editSport.html'"
        return render_template(
            'index.html', sport=editedSport, page='editSport', show_sports=sb)


@app.route('/sport/<int:sport_id>/delete/', methods=['GET', 'POST'])
def deleteSport(sport_id):
    # Function to delete an existing sport category.
    sb = querySports()
    print 'called deleteSport(sport_id)'
    sportToDelete = session.query(
        Sport).filter_by(id=sport_id).one()
    print "sportToDelete: " + str(sportToDelete)
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    if sportToDelete.user_id != login_session['user_id']:
        print "sportToDelete.user_id != login_session['user_id']"
        return "<script>function myFunction() {alert('You are not' \
        'authorized to delete this restaurant. Please create your own ' \
        'restaurant in order to ' \
        'delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print "request.method == 'POST'"
        session.delete(sportToDelete)
        flash('%s Successfully Deleted' % sportToDelete.name)
        session.commit()
        return redirect(url_for('showSports', sport_id=sport_id))
    else:
        print "request.method != 'POST'"
        print "calling 'deleteSport.html'"
        return render_template(
            'index.html', sport=sportToDelete,
            page='deleteSport', show_sports=sb)


@app.route('/sport/<int:sport_id>/')
@app.route('/sport/<int:sport_id>/items/')
def showSportItems(sport_id):
    # Function to show inventory of a certain sport category.
    sb = querySports()
    print 'called showSportItems(sport_id)'
    print 'sport_id obtained from the a href tag... '+str(sport_id)
    sport = session.query(Sport).filter_by(id=sport_id).one()
    print "sport: "+str(sport)
    items = session.query(CategoryItem).filter_by(sport_id=sport_id).all()
    print "items: "+str(items)
    return render_template(
        'index.html', items=items, sport=sport, page='menu', show_sports=sb)


# Create a new menu item
@app.route('/sport/<int:sport_id>/items/new/', methods=['GET', 'POST'])
def newSportItem(sport_id):
    # Function to add a new item to a sport category.
    sb = querySports()
    print 'called newSportItem(sport_id)'
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    print 'sport_id is ' + str(sport_id)
    sport = session.query(Sport).filter_by(id=sport_id).one()
    print 'sport: ' + str(sport)
    print 'sport user_id is ' + str(sport.user_id)
    print "login_session['user_id'] is " + str(login_session['user_id'])
    if login_session['user_id'] != sport.user_id:
        print "login_session['user_id'] != sport.user_id"
        return "<script>function myFunction()" \
            "{alert('You are not authorized to add menu items to" \
            "this restaurant. Please create your own restaurant in order" \
            "to add items.');}</script><body onload='myFunction()''>"
    else:
        print "login_session['user_id'] == sport.user_id"
        print "request.method: " + str(request.method)
        if request.method == 'POST':
            print "request.method == 'POST'"
            print 'request.form["title"]): ' + str(request.form['title'])
            print 'request.form["description"]): ' + \
                str(request.form['description'])
            print 'request.form["price"]): ' + str(request.form['price'])
            print 'request.form["category"]): ' + str(request.form['category'])
            print 'sport_id: ' + str(sport_id)
            print 'user_id: ' + str(sport.user_id)
            cd = current_date()
            print 'new_date: ' + str(cd)
            newItem = CategoryItem(
                title=request.form['title'],
                description=request.form['description'],
                price=request.form['price'],
                category=request.form['category'],
                sport_id=sport_id, user_id=sport.user_id, date=cd)
            print 'newItem created!'
            print "newItem.title: " + str(newItem.title)
            print "newItem.description: " + str(newItem.description)
            print "newItem.sport_id: " + str(newItem.sport_id)
            print "newItem.user_id: " + str(newItem.user_id)
            print "newItem.price: " + str(newItem.price)
            print "newItem.date: " + str(newItem.date)
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.title))
            return redirect(url_for('showSportItems', sport_id=sport_id))
        print "calling 'newSportItem.html'"
        return render_template(
            'index.html',
            sport_id=sport_id,
            page='newSportItem',
            show_sports=sb)


@app.route('/sport/<int:sport_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editSportItem(sport_id, item_id):
    # Function to edit an existing sport item.
    sb = querySports()
    print 'called editSportItem(sport_id, item_id)'
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    editedItem = session.query(CategoryItem).filter_by(id=item_id).one()
    sport = session.query(Sport).filter_by(id=sport_id).one()
    print "item_id: " + str(item_id)
    print "sport_id: " + str(sport_id)
    print "editedItem: " + str(editedItem)
    print "restaurant: " + str(sport)
    if login_session['user_id'] != sport.user_id:
        print "login_session['user_id'] != restaurant.user_id"
        return "<script>function myFunction() " \
               "{alert('You are not authorized to edit menu items to this" \
               "restaurant. Please create your own restaurant in order to" \
               "edit items.');}</script><body onload='myFunction()''>"
    else:
        if request.method == 'POST':
            print "request.method == 'POST'"
            if request.form['title']:
                print "request.form['title']: " + request.form['title']
                editedItem.title = request.form['title']
            if request.form['description']:
                print "request.form['description']: " + \
                        request.form['description']
                editedItem.description = request.form['description']
            if request.form['price']:
                print "request.form['price']: " + request.form['price']
                editedItem.price = request.form['price']
            session.add(editedItem)
            session.commit()
            flash('Sport Item Successfully Edited')
            return redirect(url_for('showSportItems', sport_id=sport_id))
        else:
            print "request.method != 'POST'"
            print "calling 'editsportitem.html'"
            return render_template('index.html', sport_id=sport_id,
                                   item_id=item_id, item=editedItem,
                                   page='editSportItem', show_sports=sb)


@app.route('/sport/<int:sport_id>/menu/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteSportItem(sport_id, item_id):
    # Function to delete an existing sport item.
    sb = querySports()
    print 'deleteSportItem(sport_id, item_id)'
    if 'username' not in login_session:
        print "'username' not in login_session"
        return redirect('/login')
    sport = session.query(Sport).filter_by(id=sport_id).one()
    print 'sport_id is ' + str(sport_id)
    itemToDelete = session.query(CategoryItem).filter_by(id=item_id).one()
    print 'item_id is ' + str(item_id)
    print 'itemToDelete: ' + str(itemToDelete)
    if login_session['user_id'] != sport.user_id:
        print "login_session['user_id'] != restaurant.user_id"
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete menu items to this restaurant. " \
               "Please create your own restaurant in order to delete " \
               "items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        print "request.method == 'POST'"
        session.delete(itemToDelete)
        session.commit()
        flash('Sport Item Successfully Deleted')
        return redirect(url_for('showSportItems', sport_id=sport_id))
    else:
        print "request.method != 'POST'"
        print "calling 'deleteSportItem.html'"
        return render_template('index.html', item=itemToDelete,
                               page='deleteSportItem', show_sports=sb)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
