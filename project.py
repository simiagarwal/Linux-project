import json

import random

import string

from functools import wraps

from database_setup import Base, Category, Item, User

from flask import Flask, render_template, request

from flask import flash, jsonify, make_response, redirect, url_for

from flask import session as login_session

import httplib2

from oauth2client.client import FlowExchangeError

from oauth2client.client import flow_from_clientsecrets

import requests

from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "catalog"


"""Connect to Database and create database session"""
engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

"""Route to login"""
@app.route('/login')
def showLogin():
    state = ' '.join(random.choice(
        string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

"""Facebook connect"""


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps(
            'Invalid state parameter.'),
            401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_secret']
    url = 'https: //graph.facebook.com/oauth/access_token?grant_type = \
            fb_exchange_token & client_id = %s &client_secret = %s \
            &fb_exchange_token = %s' % (app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

# Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange \
        we have to split the token first on commas and select the first index \
        which gives us the key : value for the server access token then we \
        split it on colons to pull out the actual token value and replace \
        the remaining quotes with nothing so that it can be used directly \
        in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token \
            =%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token
    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token \
            =%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

"""Facebook disconnect"""


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token\
            =%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


""" Route for Google Sign in Authentication"""


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
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)

        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')

    # Verify that user is already logged in or not

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already\
                connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']

    login_session['picture'] = data['picture']

    login_session['email'] = data['email']

    # see if user exists
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
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'\
        ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])

    return output


''' Route for disconnect Google OAuth'''


@app.route('/gdisconnect')
def gdisconnect():
    # Get the access_token
    credentials = login_session.get('credentials')
    if credentials is None:

        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application / json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s'\
        % login_session['credentials']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['state']
        flash('Logout successfully')
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(
            json.dumps(
                'Failed to revoke token for given user.',
                400))
        response.headers['Content-Type'] = 'application/json'
        return response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' in login_session:
            return f(*args, **kwargs)
        else:
            flash("You are not allowed to access there")
            return redirect(url_for('showLogin', next=request.url))
    return decorated_function


'''User helper functions'''


def createUser(login_session):
    # type: (object) -> object
    """This function creates a user in the database"""
    newUser = User(
        username=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    ''' Retrieves an object of the user by giving
        user's id(user_id) as input '''
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    ''' Retrieves the user's id by giving 'email' as input.'''
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None


"""JSON APIs to view catalog Information"""


@app.route('/catalog/JSON')
def showCatalogJSON():
    ''' This is an API endpoint. THe output is a JSON format of the details
        like Name,ID '''
    categories = session.query(Category).all()
    jsonObj = jsonify(Category=[category.serialize
                                for category in categories])
    return jsonObj


'''API Endpoint for  a Specific item'''


@app.route('/catalog/<int:category_id>/item/<int:item_id>/JSON')
def ItemJSON(category_id, item_id):
    ''' This is an API endpoint. The ouput is a JSON formatted details of
        a particular Item.
    '''
    category = session.query(Category).filter_by(id=category_id).one()

    item = session.query(Item).filter_by(id=item_id)

    if item:
        return jsonify(Item=[r.serialize for r in item])
    else:
        return jsonify({"error": "%s Not Found" % '404'})


'''API Endpoint for all categories'''


@app.route('/catalog/<int:category_id>/JSON')
def catalogMenuJSON(category_id):
    ''' This is an API endpoint. The output is a list of all the items
        in JSON format.
    '''
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()

    if category:
        return jsonify(items=[r.serialize for r in items])
    else:
        return jsonify({"error": "%s Not Found" % '404'})


"""Show the catalog"""


@app.route('/')
@app.route('/catalog/')
def showCatalog():

    categories = session.query((Category.name.distinct()).label("title"))
    titles = [row.title for row in categories.all()]
    categories = session.query(Category)
    items = session.query(Item).order_by(Item.date_added.desc()).limit(5)
    return render_template("catalog.html", titles=titles, items=items,
                           categories=categories)


"""Create a new category"""


@app.route('/catalog/new/', methods=['GET', 'POST'])
@login_required
def newCategory():
    """This method creates a new category for the catalog.It checkes if
   the user is logged in or not by using @login_required decorator. It
    then allows creating new category which takes category name and
     user is as parameters."""
    if request.method == 'POST':
        if request.form['name'] != " ":
            new_Category = Category(name=request.form['name'],
                                    user_id=login_session['user_id'])
            session.add(new_Category)
            session.commit()
            flash('New Category %s Successfully Created'
                  % new_Category.name)
            return redirect(url_for('showCatalog'))
        else:
            flash('Name fields can\'t be left blank!')
            return render_template('newcategory.html')
    else:
        return render_template('newcategory.html')


'''Edit a category'''


@app.route('/catalog/<int:category_id>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category_id):
    """ This function edit's the category name from the catalog.This function
    also checks if the editor and the creator of the category are same or not.
    If they are not then they are not allowed to edit."""

    edited_category = session.query(Category).filter_by(id=category_id).first()
    if edited_category.user_id != login_session['user_id']:
        flash("You are authorised to Edit category created by You only!")

        return redirect(url_for("showCatalog"))

    if request.method == 'POST':
        if request.form['name'] != '':
            edited_category.name = request.form['name']
            session.add(edited_category)
            session.commit()
            flash('Category Successfully Edited %s' % edited_category.
                  name)
            return redirect(url_for('showCatalog'))
        else:
            flash("Error editing category!")
            return render_template('editCategory.html',
                                   category=edited_category)
    else:
        return render_template('editcategory.html',
                               category=edited_category)


'''Delete a category'''


@app.route('/catalog/<int:category_id>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category_id):
    """
    Removes the category from the database. First the user is checked if he is
    logged in or not. Then the logged in user is checked if he was the creator
    of the particular category. Only then he is allowed to dalete it

    """

    categoryToDelete = session.query(Category).filter_by(
                                                    id=category_id).first()

    if categoryToDelete.user_id != login_session['user_id']:
        flash("You are authorised to delete category created by You!")
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        session.delete(categoryToDelete)
        session.commit()
        flash('%s Successfully Deleted' % categoryToDelete.name)
        return redirect(url_for('showCatalog'))
    else:
        return render_template('deletecategory.html',
                               category=categoryToDelete)


'''Show category items'''


@app.route('/catalog/<int:category_id>/')
@app.route('/catalog/<int:category_id>/items', methods=['GET', 'POST'])
def showItem(category_id):
    """This function displays all the items in a particular category.First it
    checks if the user is logged in or not. And based on that
    it shows the catalog differently.
    If the logged in user is also the creator of the category then he is shown
    the edit/delete item options. Otherwise only items are displayed.
    """
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()

    return render_template('items.html', items=items, category=category)

"""Get the item description """


@app.route('/catalog/<int:category_id>/item/<int:item_id>/description')
def getDescription(category_id, item_id):
    items = session.query(Item).filter_by(category_id=category_id, id=item_id)
    return render_template("itemdescription.html", items=items)


'''Create a new  item'''


@app.route('/catalog/<int:category_id>/item/new/', methods=['GET', 'POST'])
@login_required
def newItem(category_id):
    """Creats a new item for the given category.First the user is checked
        whether he is logged in or not."""
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'], category_id=category.id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New Item %s  Successfully Created' % (newItem.name))
        return redirect(url_for('showItem', category_id=category.id))
    else:
        return render_template('newitem.html', category_id=category.id)


'''Edit an item'''


@app.route('/catalog/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_id, item_id):
    """Edits the item details. The user is checked if he is authorised
    to perform the editing operation by checking if he is the creator of the
    category and also logged in or not.

    """
    editedItem = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()

    if editedItem.user_id != login_session['user_id']:
            flash("You are authorised to edit items created by you!")
            return redirect(url_for("showCatalog"))

    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('%s Item Successfully Edited' % (editedItem.name))
        return redirect(url_for('showItem',
                                category_id=editedItem.category_id))
    else:
        return render_template('edititem.html', category=category,
                               item=editedItem)
'''Delete an item'''


@app.route('/catalog/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_id, item_id):
    """Deletes an Item.The user is checked if he is authorised
    to perform thedeleting operation by checking if he isthe creator of
    the category and also logged in or not.

    """
    category = session.query(Category).filter_by(id=category_id).first()
    item = session.query(Item).filter_by(id=item_id).first()
    if item.user_id != login_session['user_id']:
        flash("You are authorised to delete items created by you!")
        return redirect(url_for("showCatalog"))
    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash('%s Item Successfully Deleted' % (item.name))
        return redirect(url_for('showItem', category_id=item.category_id))
    else:
        return render_template("deleteitem.html", item=item,
                               category=category)


@app.route("/about")
def aboutus():
    return render_template("aboutus.html")


@app.route('/partners')
def partners():
    return render_template("partners.html")


@app.route("/contactus")
def contactus():
    return render_template("contactus.html")


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
