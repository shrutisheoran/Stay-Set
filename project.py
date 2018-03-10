#   Importing required libraries

from flask import Flask, render_template, request, redirect, jsonify
from flask import url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, SubCategory, Items, Users
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


# Extracting Client's Id from client_secrets.json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Stay Set Application"

'''
    Create Engine and then bind it to the base class so that the declaratives
    can be accessed through a dbsession instance
'''
engine = create_engine(
    'postgresql://postgres:happynewid@localhost/shoppingsite')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = session.query(Category).all()
sub_categories = session.query(SubCategory).all()
all_Items = session.query(Items).all()
users = session.query(Users).all()

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    print(state)
    return render_template('login.html', STATE=state)


# Server side code for login using facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
    access_token = request.data
    '''
        Exchange client token for long-lived server-side token with
        GET/oauth/acces_token?grant-type = fb_exchange_token&
        client_id={app-id}&client_secret={app-secret}&fb_exchange
        _token={short-lived token}
    '''
    app_id = json.loads(
        open(
            'fbclientsecrets.json',
            'r').read())['web']['app_id']
    app_secret = json.loads(open('fbclientsecrets.json', 'r').read())[
        'web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # noqa
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.12/me'
    '''
        Due to formatting for the result from the server token exchange
        we have to split the token first on commas and select the first
        index which gives us the key : value for the server access token
        then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be
        used directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.12/me?access_token=%s&fields=name,id,email' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']

    # The token must be stored in login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture

    url = 'https://graph.facebook.com/v2.12/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # noqa
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data['data']['url']

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
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print("done!")
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    # Only disconnect a connected user.
    # The access_token must be included to successfully logout.
    access_token = login_session.get('access_token')
    facebook_id = login_session.get('facebook_id')
    # print(access_token)
    if facebook_id is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Execute HTTP Get request to revoke current token.
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)
    if result['status'] == '200':
        #  Reset the user's session.
        del login_session['facebook_id']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash("Successfully logged out")
        return redirect(url_for('showCatalog'))
    else:
        # For whatever reason, the given token was invalid
        flash("Not Logged out...Try Again")
        return redirect(url_for('showCatalog'))


@app.route('/gconnect', methods=['POST'])
# SERVER SIDE CODE FOR AUTHENTICATION BY GOOGLE OAuth2
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
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    print(login_session['user_id'])
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    output += 'border-radius: 150px;-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# Revoke the current user's access_token and reset login session.


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    # print(access_token)
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP Get request to revoke current token.
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result)
    if result['status'] == '200':
        #  Reset the user's session.
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['user_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash("Successfully logged out")
        return redirect(url_for('showCatalog'))
        # return response
    else:
        # For whatever reason, the given token was invalid
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        flash("Not Logged out...Try Again")
        return redirect(url_for('showCatalog'))
        # return response

# JSON APIs
# JSON API to view Categories Information


@app.route('/stayset/Corners/JSON')
def cornersJSON():
    if 'email' not in login_session:
        return redirect('/login')
    else:
        return jsonify(Corners=[c.serialize for c in categories])

# JSON API to view ALL Items Information


@app.route('/stayset/Items/JSON')
def itemsJSON():
    if 'email' not in login_session:
        return redirect('/login')
    else:
        return jsonify(Items=[i.serialize for i in all_Items])

# JSON API to view Specified Category's Subcategories Information


@app.route('/stayset/<string:category_name>/SubCategories/JSON')
def subCategoriesJSON(category_name):
    if 'email' not in login_session:
        return redirect('/login')
    else:
        corner = session.query(Category).filter_by(name=category_name).one()
        sub_category = session.query(SubCategory).filter_by(
            category_id=corner.id).all()
        return jsonify(Sub_Categories=[sc.serialize for sc in sub_category])

# JSON API to view Specified Items Information


@app.route('/stayset/<string:category_name>/<string:sub_category_name>/Items/JSON')  # noqa
def ItemsJSON(category_name, sub_category_name):
    if 'email' not in login_session:
        return redirect('/login')
    else:
        corner = session.query(Category).filter_by(name=category_name).one()
        sub_category = session.query(SubCategory).filter_by(
            category_id=corner.id, name=sub_category_name).one()
        SubCategoryItems = session.query(Items).filter_by(
            subCategory_id=sub_category.id).all()
        return jsonify(Items=[sci.serialize for sci in SubCategoryItems])

# Create the ITEM CATALOG HOME page


@app.route('/')
@app.route('/stayset/')
def showCatalog():
    items = session.query(Items).all()
    # Only allow a logged in user to add a corner
    if 'email' not in login_session:
        return render_template('catalog.html', categories=categories,
                               sub_categories=sub_categories, items=items,
                               login=0)
    else:
        return render_template('catalog.html', categories=categories,
                               sub_categories=sub_categories, items=items,
                               login=1, username=login_session['username'],
                               users=users)

# To add a new Corner


@app.route('/addcorner/', methods=['GET', 'POST'])
def addCorner():
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCorner = Category(name=request.form['name'],
                             picture=request.form['image'],
                             user_id=login_session['user_id'])
        session.add(newCorner)
        flash("New Corner %s Successfully Created" % newCorner.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('addcorner.html',
                               username=login_session['username'])

# To edit an existing corner


@app.route('/editcorner/<string:name>/', methods=['GET', 'POST'])
def editCorner(name):
    if 'email' not in login_session:
        return redirect('/login')
    editCorner = session.query(Category).filter_by(name=name).one()
    if request.method == 'POST':
        editCorner.picture = request.form['image']
        session.add(editCorner)
        flash("Corner %s Successfully Editd" % editCorner.name)
        session.commit()
        return redirect(url_for('showCorner', category_name=name))
    else:
        return render_template('editcorner.html', editCorner=editCorner,
                               username=login_session['username'])

# To remove an existing corner


@app.route('/remove/<string:name>/', methods=['GET', 'POST'])
def removeCorner(name):
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        corner = session.query(Category).filter_by(name=name).one()
        session.delete(corner)
        session.commit()
        flash("Corner successfully deleted")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('removecorner.html', name=name,
                               username=login_session['username'])


# TO SHOW THE SPECIFIED CORNER
@app.route('/showcorner/<string:category_name>/')
def showCorner(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    sub_category = session.query(SubCategory).filter_by(
        category_id=category.id).all()
    creator = getUserInfo(category.user_id)
    if 'email' not in login_session:
        return render_template('sub_category.html', sub_category=sub_category,
                               category=category, categories=categories,
                               sub_categories=sub_categories, login=0)
    # Only allow the creator of the corner to edit and remove it.
    if creator.id != login_session['user_id']:
        return render_template('sub_category.html', sub_category=sub_category,
                               category=category, categories=categories,
                               sub_categories=sub_categories, login=1,
                               username=login_session['username'], users=users)
    else:
        return render_template('sub_category.html', sub_category=sub_category,
                               category=category, categories=categories,
                               sub_categories=sub_categories, login="creator",
                               username=login_session['username'], users=users)

# To add a new subcategory to a corner


@app.route('/new_subcategory/<string:category_name>/', methods=['GET', 'POST'])
def addSubCategory(category_name):
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        corner = session.query(Category).filter_by(name=category_name).one()
        sub = SubCategory(
            name=request.form['name'],
            picture=request.form['image'],
            category_id=corner.id,
            user_id=login_session['user_id'])
        session.add(sub)
        flash("Sub-Category Successfully Added")
        session.commit()
        return redirect(url_for('showCorner', category_name=category_name))
    else:
        return render_template('addsubcategory.html', name=category_name,
                               username=login_session['username'])

# To edit an existing subcategory


@app.route(
    '/edit_subcategory/<string:category_name>/<string:sub_category_name>/',
    methods=[
        'GET',
        'POST'])
def editSubCategory(category_name, sub_category_name):
    if 'email' not in login_session:
        return redirect('/login')
    corner = session.query(Category).filter_by(name=category_name).one()
    sub_category = session.query(SubCategory).filter_by(
        category_id=corner.id, name=sub_category_name).one()
    if request.method == 'POST':
        sub_category.picture = request.form['image']
        session.add(sub_category)
        flash("Sub-Category successfully edited")
        session.commit()
        return redirect(url_for('showCorner', category_name=category_name))
    else:
        return render_template('edit_subcategory.html', corner=category_name,
                               sub_category=sub_category,
                               username=login_session['username'])

# To remove an existing subcategory


@app.route(
    '/remove_subcategory/<string:category_name>/<string:sub_category_name>/',
    methods=[
        'GET',
        'POST'])
def removeSubCategory(category_name, sub_category_name):
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        corner = session.query(Category).filter_by(name=category_name).one()
        sub_category = session.query(SubCategory).filter_by(
            category_id=corner.id, name=sub_category_name).one()
        session.delete(sub_category)
        flash("Item successfully deleted")
        session.commit()
        return redirect(url_for('showCorner', category_name=category_name))
    else:
        return render_template('remove_subcategory.html', corner=category_name,
                               sub_category=sub_category_name,
                               username=login_session['username'])


# TO SHOW ITEMS OF THE SPECIFIED CATEGORY AND SUBCATEGORY
@app.route('/showitems/<string:category_name>/<string:sub_category_name>/')
def showItems(category_name, sub_category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    sub_category = session.query(SubCategory).filter_by(
        category_id=category.id, name=sub_category_name).one()
    items = session.query(Items).filter_by(
        category_id=category.id,
        subCategory_id=sub_category.id).all()
    creator = getUserInfo(sub_category.user_id)
    if 'email' not in login_session:
        return render_template('items.html', corner=category.name,
                               sub_category=sub_category,
                               items=items, categories=categories,
                               sub_categories=sub_categories, login=0)
    # Only allow the creator of the subcategory to edit and remove it
    if creator.id != login_session['user_id']:
        return render_template('items.html', corner=category.name,
                               sub_category=sub_category,
                               items=items, categories=categories,
                               sub_categories=sub_categories, login=1,
                               username=login_session['username'],
                               users=users)
    else:
        return render_template('items.html', corner=category.name,
                               sub_category=sub_category, items=items,
                               categories=categories,
                               sub_categories=sub_categories,
                               login="creator",
                               username=login_session['username'],
                               users=users)

# Show a specified item's details


@app.route(
    '/showitem/<string:category_name>/<string:sub_category_name>/<string:item_name>/',  # noqa
    methods=[
        'GET',
        'POST'])
def showItem(category_name, sub_category_name, item_name):
    items = session.query(Items).all()
    corner = session.query(Category).filter_by(name=category_name).one()
    sub_category = session.query(SubCategory).filter_by(
        category_id=corner.id, name=sub_category_name).one()
    item = session.query(Items).filter_by(category_id=corner.id,
                                          subCategory_id=sub_category.id,
                                          name=item_name).one()
    creator = getUserInfo(item.user_id)
    if 'email' not in login_session:
        return render_template('item_detail.html', categories=categories,
                               sub_categories=sub_categories,
                               corner=category_name,
                               sub_category=sub_category_name, item=item,
                               email=creator.email, login=0)
    # Only allow the creator of the item to edit and delete it
    if creator.id != login_session['user_id']:
        return render_template('item_detail.html', categories=categories,
                               sub_categories=sub_categories,
                               corner=category_name,
                               sub_category=sub_category_name, item=item,
                               email=creator.email, login=1,
                               username=login_session['username'], users=users)
    else:
        return render_template('item_detail.html', categories=categories,
                               sub_categories=sub_categories,
                               corner=category_name,
                               sub_category=sub_category_name, item=item,
                               email=creator.email, login="creator",
                               username=login_session['username'], users=users)


# Add new item
@app.route(
    '/addnewitem/<string:category_name>/<string:sub_category_name>/',
    methods=[
        'GET',
        'POST'])
def addItem(category_name, sub_category_name):
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        corner = session.query(Category).filter_by(name=category_name).one()
        sub_category = session.query(SubCategory).filter_by(
            category_id=corner.id, name=sub_category_name).one()
        additem = Items(
            name=request.form['item_name'],
            picture=request.form['image'],
            price=request.form['price'],
            seller_name=request.form['seller_name'],
            seller_phoneno=request.form['seller_phoneno'],
            description=request.form['description'],
            user_id=login_session['user_id'],
            category_id=corner.id,
            subCategory_id=sub_category.id)
        session.add(additem)
        flash("Item successfully added")
        session.commit()
        return redirect(url_for('showItems', category_name=category_name,
                                sub_category_name=sub_category_name))
    else:
        return render_template('addnewitem.html', corner=category_name,
                               sub_category=sub_category_name,
                               user=login_session['username'])

# To edit an existing item


@app.route(
    '/edititem/<string:category_name>/<string:sub_category_name>/<string:item_name>/',  # noqa
    methods=[
        'GET',
        'POST'])
def editItem(category_name, sub_category_name, item_name):
    if 'email' not in login_session:
        return redirect('/login')
    corner = session.query(Category).filter_by(name=category_name).one()
    sub_category = session.query(SubCategory).filter_by(
        category_id=corner.id, name=sub_category_name).one()
    item = session.query(Items).filter_by(category_id=corner.id,
                                          subCategory_id=sub_category.id,
                                          name=item_name).one()
    if request.method == 'POST':
        item.price = request.form['price']
        item.picture = request.form['image']
        item.seller_name = request.form['seller_name']
        item.seller_phoneno = request.form['seller_phoneno']
        item.description = request.form['description']
        session.add(item)
        session.commit()
        return redirect(url_for('showItem', category_name=category_name,
                                sub_category_name=sub_category_name,
                                item_name=item_name))
    else:
        return render_template('edititem.html', corner=corner,
                               sub_category=sub_category, item=item,
                               username=login_session['username'])


# Remove an existing item
@app.route(
    '/removeitem/<string:category_name>/<string:sub_category_name>/<string:item_name>/',  # noqa
    methods=[
        'GET',
        'POST'])
def removeItem(category_name, sub_category_name, item_name):
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        corner = session.query(Category).filter_by(name=category_name).one()
        sub_category = session.query(SubCategory).filter_by(
            category_id=corner.id, name=sub_category_name).one()
        item = session.query(Items).filter_by(category_id=corner.id,
                                              subCategory_id=sub_category.id,
                                              name=item_name).one()
        delete_item = session.query(Items).filter_by(id=item.id).one()
        session.delete(delete_item)
        flash("Item successfully deleted")
        session.commit()
        return redirect(url_for('showItems', category_name=category_name,
                                sub_category_name=sub_category_name))
    else:
        return render_template('removeitem.html', corner=category_name,
                               sub_category=sub_category_name,
                               item_name=item_name,
                               username=login_session['username'])


# Takes an email address and returns user_id
def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except BaseException:
        return None

# Returns user object for the provided user_id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user

# Enter logged user info in user table in database and returns user_id


def createUser(login_session):
    newUser = Users(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id

# To disconnect a connected user


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        #  Reset the user's session.
        if login_session['provider'] == 'google':
            return redirect(url_for('gdisconnect'))
        if login_session['provider'] == 'facebook':
            return redirect(url_for('fbdisconnect'))
        return None
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


if __name__ == '__main__':
    app.secret_key = 'my*_*hidden*_*key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
