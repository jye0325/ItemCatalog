from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask import flash
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(open('/var/www/ItemCatalog/ItemCatalog/client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "ItemCatalog"

engine = create_engine('sqlite:////var/www/ItemCatalog/ItemCatalog/main.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Routing for login
@app.route('/login/')
def login():
    """ Creates a state token, (32) characters long, to prevent request
    forgery."""
    state = ''.join(random.choice(string.ascii_uppercase+string.digits)
                    for x in xrange(32))
    login_session['state'] = state
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
        response = make_response(json.dumps('Failed to upgrade authorization \
                                            code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid
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
        response = make_response(json.dumps("Token's user ID does not match \
                                            given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID does not match \
                                            app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already \
                                            connected.'), 200)
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

    # See if user exists, if it doesn't create new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;\
                            border-radius: 150px;-webkit-border-radius: 150px;\
                            -moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    if(login_session['email'] == "jye0325@gmail.com"):
        newUser = User(name=login_session['username'],
                       email=login_session['email'],
                       picture=login_session['picture'], status='admin')
    else:
        newUser = User(name=login_session['username'],
                       email=login_session['email'],
                       picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Routing for logout
@app.route('/logout/')
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
        % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given \
                                 user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Routing for main menu
@app.route('/')
@app.route('/main/')
def mainMenu():
    """Returns a list of categories in the menu pane and the latest 5 added \
    items in the item pane."""
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(desc(Item.id)).limit(5)
    if 'username' in login_session:
        return render_template('main.html', categories=categories,
                               latestItems=latestItems, loggedIn=True)
    else:
        return render_template('main.html', categories=categories,
                               latestItems=latestItems)


@app.route('/main/<int:category_id>/')
def categoryItems(category_id):
    """Updates the item pane with a list of items specific to that category"""
    categories = session.query(Category).all()
    items = session.query(Item).filter_by(category_id=category_id)
    if 'username' in login_session:
        return render_template('main.html', categories=categories,
                               items=items, category_id=category_id,
                               loggedIn=True)
    else:
        return render_template('main.html', categories=categories, items=items,
                               category_id=category_id)


@app.route('/main/newCategory/', methods=['GET', 'POST'])
def newCategory():
    """Creates a new category -- Requires Admin Privileges"""
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).one()
    if user.status != 'admin':
        return "<script>function myFunction() {alert('Sorry only admin \
                privileges are allowed to add new categories for now.');\
                location.href='http://localhost:5000';}</script><body onload=\
                'myFunction()'>"
    if request.method == 'POST':
        category = Category(name=request.form['name'],
                            user_id=login_session['user_id'])
        session.add(category)
        session.commit()
        flash('Successfully added new category, ' + category.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('newCategory.html')


@app.route('/main/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    """Edits a specified category."""
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if category.user_id == user.id or user.status == 'admin':
        pass
    else:
        return "<script>function myFunction() {alert('Sorry only the creator \
                of this category, or an admin, can edit this.');\
                location.href='http://localhost:5000';}</script>\
                <body onload='myFunction()'>"
    if request.method == 'POST':
        category.name = request.form['name']
        session.add(category)
        session.commit()
        flash('Successfully editted category, ' + category.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('editCategory.html',
                               category=category, id=category_id)


@app.route('/main/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """Deletes a specific category."""
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if category.user_id == user.id or user.status == 'admin':
        pass
    else:
        return "<script>function myFunction() {alert('Sorry only the creator \
                of this category, or an admin, can delete this.');\
                location.href='http://localhost:5000';}</script>\
                <body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(category)
        session.commit()
        flash('Successfully deleted category, ' + category.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('deleteCategory.html',
                               category=category, id=category_id)


# Routing for item menu
@app.route('/main/<int:category_id>/item/<int:item_id>/')
def itemMenu(category_id, item_id):
    """Returns details about the particular item in the item page"""
    category = session.query(Category).filter_by(category_id=category_id).one()
    item = session.query(Item).filter_by(category_id=category_id,
                                         id=item_id).one()
    return render_template('item.html', category=category, item=item)


@app.route('/main/<int:category_id>/newItem/', methods=['GET', 'POST'])
def newItem(category_id):
    """Creates a new item for a specified category."""
    if 'username' not in login_session:
        return redirect('/login')
    categories = session.query(Category).all()
    if request.method == 'POST':
        item = Item(name=request.form['name'],
                    category_id=request.form['category'],
                    description=request.form['description'],
                    user_id=login_session['user_id'])
        session.add(item)
        session.commit()
        flash('Successfully added new item, ' + item.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('newItem.html', id=category_id,
                               categories=categories)


@app.route('/main/<int:category_id>/item/<int:item_id>/edit/',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """Edit the details about the particular item"""
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(category_id=category_id,
                                         id=item_id).one()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if item.user_id == user.id or user.status == 'admin':
        pass
    else:
        return "<script>function myFunction() {alert('Sorry only the creator \
                of this item, or an admin, can edit this.');\
                location.href='http://localhost:5000';}</script>\
                <body onload='myFunction()'>"
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        flash('Successfully editted item, ' + item.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('editItem.html', item=item,
                               id=category_id, item_id=item_id)


@app.route('/main/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """Deletes the particular item"""
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(category_id=category_id,
                                         id=item_id).one()
    user = session.query(User).filter_by(email=login_session['email']).one()
    if item.user_id == user.id or user.status == 'admin':
        pass
    else:
        return "<script>function myFunction() {alert('Sorry only the creator \
                of this item, or an admin, can delete this.');\
                location.href='http://localhost:5000';}</script>\
                <body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Successfully deleted item, ' + item.name)
        return redirect(url_for('mainMenu'))
    else:
        return render_template('deleteItem.html', item=item,
                               id=category_id, item_id=item_id)


@app.route('/status')
def statusChange():
    """For evaluation purposes, this will change the privileges from user to
    admin, or vice-versa."""
    if 'username' not in login_session:
        return redirect('/login')
    user = session.query(User).filter_by(email=login_session['email']).one()
    if user.status == 'admin':
        user.status = 'user'
        session.add(user)
        session.commit()
        flash('Successfully converted, ' + user.name + ' to user privileges')
        return redirect(url_for('mainMenu'))
    elif user.status == 'user':
        user.status = 'admin'
        session.add(user)
        session.commit()
        flash('Successfully converted, ' + user.name + ' to admin privileges')
        return redirect(url_for('mainMenu'))
    else:
        flash('Unknown error. Please try again!')
        return redirect(url_for('mainMenu'))


# JSON Routes
@app.route('/main/JSON')
def mainMenuJSON():
    """Serializes all the categories"""
    category = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in category])


@app.route('/main/<int:category_id>/item/JSON')
def itemMenuJSON(category_id):
    """Serializes all the items within a particular category"""
    category = session.query(Category).all()
    item = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(Item=[i.serialize for i in item])


@app.route('/main/<int:category_id>/item/<int:item_id>/JSON')
def specificItemJSON(category_id, item_id):
    """Serializes a specific item in a specific category"""
    category = session.query(Category).all()
    item = session.query(Item).filter_by(id=item_id,
                                         category_id=category_id).one()
    return jsonify(Item=item.serialize)


@app.route('/user/JSON')
def userJSON():
    """This is a test JSON to see that users are being created properly"""
    user = session.query(User).all()
    return jsonify(User=[i.serialize for i in user])


if __name__ == '__main__':
    app.secret_key = 'root'
    app.debug = True
    app.run()

